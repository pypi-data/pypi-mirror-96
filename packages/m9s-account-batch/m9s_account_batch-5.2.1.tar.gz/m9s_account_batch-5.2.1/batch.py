# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import copy
from decimal import Decimal
from time import *

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.pool import Pool
from trytond.rpc import RPC
from trytond.pyson import Get, Equal, Eval, Not, In, Bool, Or, And, If, \
    PYSONEncoder
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.i18n import gettext

_STATES = {
    'readonly': Equal(Eval('state'), 'closed'),
    }
_DEPENDS = ['state']

_LINE_STATES = {
    'readonly': Or(
        Not(Bool(Eval('journal'))),
        (Equal(Eval('state'), 'posted'))
        )
    }
_LINE_DEPENDS = ['journal', 'state']
_ZERO = Decimal('0.0')


class Batch(Workflow, ModelSQL, ModelView):
    'Account Batch'
    __name__ = 'account.batch'

    name = fields.Char('Name', required=True, states=_STATES,
        depends=['state'])
    company = fields.Many2One('company.company', 'Company', required=True,
        select=True, states=_STATES, domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        depends=_DEPENDS)
    journal = fields.Many2One('account.batch.journal', 'Journal',
        required=True, states={
            'readonly': Or(
                Bool(Eval('lines')),
                Equal(Eval('state'), 'closed')
                ),
        }, domain=[
            ('company', '=', Eval('context', {}).get('company', -1)),
        ], select=True, depends=_DEPENDS + ['journal_type', 'lines'])
    lines = fields.One2Many('account.batch.line', 'batch',
            'Batch Lines', add_remove=[],
        # XXX 'bool' object is not iterable (<type 'exceptions.TypeError'>)
        #And(
        #    Or(
        #        Not(Bool(Eval('batch'))),
        #        Equal(Eval('active_id'), Eval('batch'))
        #    ),
        #    Bool(('journal', '=', Eval('journal')))
        #    )],
            context={
                'journal': Eval('journal'),
                }, states=_STATES, depends=_DEPENDS)
    move_lines = fields.Function(fields.One2Many('account.move.line',
            None, 'Move Lines'), 'get_move_lines')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')
    journal_type = fields.Function(fields.Selection('selection_journal_types',
            'Journal'), 'get_journal_type')
    state = fields.Selection([
            ('open', 'Open'),
            ('closed', 'Closed'),
            ], 'State', readonly=True)

    @classmethod
    def __setup__(cls):
        super(Batch, cls).__setup__()
        cls._transitions |= set((
                ('open', 'closed'),
                ))
        cls._buttons.update({
                'close': {
                    'invisible': Eval('state') != 'open',
                    },
                })
        cls.__rpc__.update({'selection_journal_types': RPC(False)})

    def get_rec_name(self, name):
        name = ' - ' + self.name if self.name else ''
        return self.journal.name + name

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_state():
        return 'open'

    @staticmethod
    def default_currency_digits():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.digits
        return 2

    @fields.depends('journal')
    def on_change_with_currency_digits(self, name=None):
        if self.journal:
            return self.journal.currency.digits
        return 2

    @fields.depends('journal')
    def on_change_journal(self):
        BatchLine = Pool().get('account.batch.line')
        if self.journal:
            self.journal_type = self.journal.account_journal.type
            account_journal = self.journal.account_journal
            # For correct start balance check of bank batches there may be no
            # unposted batch lines for same accounts
            if account_journal.type in ['bank', 'cash']:
                account_id = (self.journal.account
                    and self.journal.account.id or None)
                if account_id:
                    lines = (BatchLine.check_unposted_batch_lines_for_account(
                                    [self.journal.account.id]))
                    if lines:
                        raise UserError(
                            gettext('account_batch.unposted_lines'))

            # Check for configured accounts on journal
            if (not account_journal.type == 'general'
                    and not self.journal.account):
                raise UserError(gettext(
                        'account_batch.missing_journal_account'))

    def get_start_balance(self, running=False):
        res = self._account_balance(self.journal.account)
        if running:
            res += self.get_lines_sum()
        return res

    def get_lines_sum(self):
        res = _ZERO
        for line in self.lines:
            if line.amount:
                if line.is_cancelation_move:
                    res -= line.amount
                else:
                    res += line.amount
        return res

    def _account_balance(self, account=None):
        Account = Pool().get('account.account')
        if not account:
            return _ZERO
        with Transaction().set_context(no_rounding=True):
            account = Account(account.id)
        return account.balance

    @classmethod
    def get_journal_type(cls, batches, name):
        res = {}
        for batch in batches:
            res[batch.id] = batch.journal.account_journal.type
        return res

    @classmethod
    def selection_journal_types(cls):
        AccountJournal = Pool().get('account.journal')
        return AccountJournal.type.selection

    @classmethod
    def get_move_lines(cls, batches, name):
        res = {}
        for batch in batches:
            res[batch.id] = []
            for line in batch.lines:
                for move_line in line.move.lines:
                    res[batch.id].append(move_line.id)
        return res

    @classmethod
    def copy(cls, batches, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('state', cls.default_state())
        default.setdefault('lines', None)

        # should we add copies of lines?
        #new_batches = []
        #for batch in batches:
        #    default['name'] = batch['name'] + ' copy'
        #    new_batch, = super(cls, cls).copy([batch], default=default)
        #    print(new_batch)
        #    Line.copy(batch.lines, default={
        #            'batch': new_batch.id,
        #            })
        #    new_batches.append(new_batch)
        #return new_batches
        return super(Batch, cls).copy(batches, default=default)

    @classmethod
    @ModelView.button
    @Workflow.transition('closed')
    def close(cls, batches):
        BatchLine = Pool().get('account.batch.line')

        lines = [l for b in batches for l in b.lines]
        BatchLine.post(lines)
        cls.write(batches, {
                'state': 'closed',
                })

    @classmethod
    def view_header_get(cls):
        '''
        view_header_get was removed in 4.2

        We keep this stub that can be called for custom view headers
        '''
        pool = Pool()
        Batch = pool.get('account.batch')
        BatchJournal = pool.get('account.batch.journal')
        Company = pool.get('company.company')
        Fiscalyear = pool.get('account.fiscalyear')
        Period = pool.get('account.period')
        Translation = pool.get('ir.translation')

        context = Transaction().context
        lang_code = 'en_US'
        if context.get('company'):
            company = Company(context['company'])
            if company.party.lang:
                lang_code = company.party.lang.code

        def get_translated_item(source, model, lang_code):
            return (Translation.get_source(model, 'field', lang_code, source)
                or source)

        batch_string = journal_string = period_string = year_string = ''
        if context.get('journal'):
            trans_journal = get_translated_item('Journal',
                'account.batch.line,journal', lang_code)
            batch_journal = BatchJournal(context['journal'])
            journal_string = '%s: %s' % (trans_journal, batch_journal.rec_name)
        if context.get('batch'):
            trans_batch = get_translated_item('Batch',
                'account.batch.line,batch', lang_code)
            batch = Batch(context['batch'])
            batch_string = '%s: %s' % (trans_batch, batch.name)
        if context.get('period'):
            trans_period = get_translated_item('Period',
                'account.journal.period,period', lang_code)
            period = Period(context['period'])
            period_string = '%s: %s' % (trans_period, period.name)
        elif context.get('fiscalyear'):
            trans_fiscalyear = get_translated_item('Fiscal Year',
                'account.batch.line,fiscalyear', lang_code)
            fiscalyear = Fiscalyear(context['fiscalyear'])
            year_string = '%s: %s' % (trans_fiscalyear, fiscalyear.name)
        return ' | '.join([_f for _f in [
            batch_string,
            journal_string,
            period_string,
            year_string] if _f])


class BatchLine(ModelSQL, ModelView):
    'Account Batch Line'
    __name__ = 'account.batch.line'

    sequence = fields.Char('Seq.', readonly=True,
            help='Chronological sequence of batch lines by creation date')
    code = fields.Char('Code', readonly=True,
            help='Chronological sequence of batch lines by posting date')
    posting_text = fields.Char('Posting Text', states=_LINE_STATES,
            depends=_LINE_DEPENDS, select=True)
    batch = fields.Many2One('account.batch', 'Batch', ondelete='CASCADE',
            domain=[('journal', '=', Eval('journal'))], states={
                'readonly': Or(
                    Equal(Eval('state'), 'posted'),
                    Not(Bool(Eval('journal'))),
                    Bool(Get(Eval('context', {}), 'batch', 0))
                    )
            }, depends=['state', 'journal'], select=True)
    journal = fields.Many2One('account.batch.journal', 'Batch Journal',
            required=True, states={
                'readonly': Or(
                    Equal(Eval('state'), 'posted'),
                    Bool(Eval('journal')),
                    Bool(Get(Eval('context', {}), 'journal', 0))
                    )
            }, depends=['state', 'journal'], select=True)
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
            states=_LINE_STATES, depends=_LINE_DEPENDS)
    date = fields.Date('Date', required=True, states=_LINE_STATES,
        depends=_LINE_DEPENDS, select=True)
    amount = fields.Numeric('Amount', required=True,
            digits=(16, Eval('currency_digits', 2)),
            depends=_LINE_DEPENDS+['currency_digits'],
            states=_LINE_STATES)
    account = fields.Many2One('account.account', 'Account', required=True,
        domain=[
            ('type', '!=', None),
            ('closed', '!=', True),
            ],
        states={
            'readonly':
                Or(
                    Or(
                        In(Eval('journal_type'), ['cash', 'bank']),
                        Not(Bool(Eval('journal_type', False)))
                    ),
                    Equal(Eval('state'), 'posted')
                )
        }, depends=['journal_type', 'state'])
    contra_account = fields.Many2One('account.account', 'Contra Account',
        required=True,
        domain=[
            ('type', '!=', None),
            ('closed', '!=', True),
            ],
        states=_LINE_STATES,
        depends=_LINE_DEPENDS)
    side_account = fields.Function(fields.Selection([
                ('', ''),
                ('debit', 'D'),
                ('credit', 'C'),
                ], ' ',
            help="'D': Account is debit side\n"
            "'C': Account is credit side"),
            'get_function_fields')
    side_contra_account = fields.Function(fields.Selection([
                ('', ''),
                ('debit', 'D'),
                ('credit', 'C'),
                ], ' ',
            help="'D': Contra Account is debit side\n"
            "'C': Contra Account is credit side"),
            'get_function_fields')
    party = fields.Many2One('party.party', 'Party', states=_LINE_STATES,
        depends=_LINE_DEPENDS)
    is_cancelation_move = fields.Boolean('Cancelation',
        states=_LINE_STATES, depends=_LINE_DEPENDS,
        help='Create an inverted move for an inverted amount '
        'to compensate for a same move with original amount.')
    move = fields.Many2One('account.move', 'Account Move', readonly=True,
            select=True)
    reference = fields.Char('Reference', select=True,
            states=_LINE_STATES, depends=_LINE_DEPENDS,
            help='This field collects references to external documents, '
            'like voucher or receipt numbers.')
    maturity_date = fields.Date('Maturity Date', states=_LINE_STATES,
            depends=_LINE_DEPENDS, help='Date to pay the amount of the '
            'batch line at least.')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_function_fields')
    journal_type = fields.Function(fields.Char('Batch Journal Type'),
            'get_function_fields')
    state = fields.Function(fields.Selection([
                ('staging', 'Staging'),
                ('draft', 'Draft'),
                ('posted', 'Posted'),
            ], 'State'), 'get_function_fields',
            searcher='search_state')
    invoice = fields.Many2One('account.invoice', 'Invoice',
        domain=[
            ('party', If(Bool(Eval('party')), '=', '!='), Eval('party')),
            ('state', 'in',
                If(
                    In(Eval('state'), ['staging', 'draft']),
                    ['draft', 'validated', 'posted'], ['posted', 'paid']
                    )
                ),
            ],
        states={
            'readonly':
            Or(Bool(Eval('tax')),
                Or(
                    In(Get(Eval('_parent_batch', {}), 'journal_type'),
                        ['revenue', 'expense']),
                    And(
                        Not(In(Get(Eval('_parent_batch', {}), 'journal_type'),
                                ['revenue', 'expense'])),
                        Bool(_LINE_STATES['readonly']))
                    )
                ),
            },
        depends=_LINE_DEPENDS + ['party', 'tax'])
    tax = fields.Many2One('account.tax', 'Tax',
        domain=[
            ('parent', '=', None)
            ],
        states={'readonly':
                Or(Bool(Eval('invoice')),
                    _LINE_STATES['readonly'],
                )
            },
        depends=_LINE_DEPENDS + ['invoice'])

    @classmethod
    def __setup__(cls):
        super(BatchLine, cls).__setup__()
        # batch is in excludes to avoid general update of all moves.
        cls._check_modify_exclude = {'batch', 'sequence'}
        cls._order[0] = ('id', 'DESC')

    def get_rec_name(self, name):
        return ', '.join([_f for _f in [
                    self.sequence,
                    self.party.rec_name if self.party else None,
                    self.journal.rec_name,
                    str(self.date) if self.date else None] if _f])

    @classmethod
    def fields_view_get(cls, view_id=None, view_type='form'):
        res = super(BatchLine, cls).fields_view_get(view_id=view_id,
                view_type=view_type)
        res = copy.copy(res)
        context = Transaction().context
        if res['type'] == 'tree':
            if context.get('journal'):
                res['arch'] = res['arch'].replace('<field name="journal"',
                        '<field name="journal" tree_invisible="1"')
            if context.get('batch'):
                res['arch'] = res['arch'].replace('<field name="batch"',
                        '<field name="batch" tree_invisible="1"')
        return res

    @classmethod
    def default_get(cls, fields, with_rec_name=True):
        pool = Pool()
        BatchJournal = pool.get('account.batch.journal')
        Fiscalyear = pool.get('account.fiscalyear')
        Date = pool.get('ir.date')
        today = Date.today()

        values = super(BatchLine, cls).default_get(fields,
                with_rec_name=with_rec_name)

        values = values.copy()
        date = values.get('date', today)
        context = Transaction().context
        company_id = context.get('company', False)
        if 'fiscalyear' in fields:
            values['fiscalyear'] = Fiscalyear.find(company_id, date=date,
                    exception=True)

        if context.get('batch'):
            if 'batch' in fields:
                values['batch'] = context['batch']

        if context.get('journal'):
            journal = BatchJournal(context['journal'])
            account_journal = journal.account_journal
            side = cls._choose_side(_ZERO, account_journal)
            if 'journal' in fields:
                values['journal'] = context.get('journal')

            if 'account' in fields:
                values['account'] = journal.account

            if 'side_account' in fields:
                values['side_account'] = side

            if 'side_contra_account' in fields:
                values['side_contra_account'] = cls._opposite(side)

            if 'journal_type' in fields:
                values['journal_type'] = account_journal.type
        return values

    @staticmethod
    def default_sequence():
        return ''

    @staticmethod
    def default_date():
        pool = Pool()
        Period = pool.get('account.period')
        Fiscalyear = pool.get('account.fiscalyear')
        Date = pool.get('ir.date')
        Move = pool.get('account.move')
        BatchJournal = pool.get('account.batch.journal')

        res = Date.today()
        context = Transaction().context
        if not context.get('journal'):
            return res

        account_journal_id = BatchJournal(
                context['journal']).account_journal.id

        if context.get('period'):
            period = Period(context['period'])
            args = [
                ('journal', '=', account_journal_id),
                ('date', '>', period.start_date),
                ('date', '<', period.end_date)
                ]
            moves = Move.search(args, limit=1, order=[('date', 'DESC')])
            if moves:
                res = moves[0].date
            else:
                res = period.start_date
        elif context.get('fiscalyear'):
            fiscalyear = Fiscalyear(
                    context['fiscalyear'])
            args = [
                ('journal', '=', account_journal_id),
                ('date', '>', fiscalyear.start_date),
                ('date', '<', fiscalyear.end_date)
                ]
            moves = Move.search(args, limit=1, order=[('date', 'DESC')])
            if moves:
                res = moves[0].date
            else:
                res = fiscalyear.start_date
        return res

    @staticmethod
    def default_side_account():
        return ''

    @staticmethod
    def default_side_contra_account():
        return ''

    @staticmethod
    def default_currency_digits():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.digits
        return 2

    @staticmethod
    def default_state():
        return 'staging'

    @classmethod
    def _opposite(cls, side):
        opposite = ''
        if side == 'debit':
            opposite = 'credit'
        elif side == 'credit':
            opposite = 'debit'
        return opposite

    @fields.depends('amount', 'journal', 'side_account')
    def on_change_with_side_contra_account(self, name=None):
        return self.__class__._opposite(self.side_account)

    @fields.depends('amount', 'journal', 'side_account')
    def on_change_with_side_account(self, name=None):
        if self.journal:
            account_journal = self.journal.account_journal
            side = self.__class__._choose_side(self.amount or _ZERO,
                account_journal)
            return side

    @classmethod
    def _choose_side(cls, amount, account_journal):
        if account_journal.type in ['general', 'revenue', 'cash', 'bank']:
            if amount >= _ZERO:
                side = 'debit'
            else:
                side = 'credit'
        else:
            if amount >= _ZERO:
                side = 'credit'
            else:
                side = 'debit'
        return side

    @fields.depends('account', 'contra_account', 'invoice')
    def on_change_account(self):
        if self.account == self.contra_account:
            self.account = None
        if self.invoice:
            if self.account:
                if self.account != self.invoice.account:
                    self.invoice = None
            else:
                self.account = self.invoice.account.id

    @fields.depends('account', 'contra_account')
    def on_change_contra_account(self):
        if self.account == self.contra_account:
            self.contra_account = None
        if self.contra_account:
            taxes = self.contra_account.taxes
            if taxes and len(taxes) == 1:
                self.tax = taxes[0].id

    @fields.depends('party', 'journal', 'amount', 'invoice', 'contra_account',
        'tax')
    def on_change_party(self):
        # Set the default accounts when there is no contra_account or tax set
        if (self.party and self.journal and (
                    not self.contra_account or not self.tax)):
            if self.amount:
                type_ = self.journal.account_journal.type
                if type_ == 'expense':
                    self.account = self.party.account_payable.id
                elif type_ == 'revenue':
                    self.account = self.party.account_receivable.id
                elif type_ in ['cash', 'bank']:
                    if self.amount >= _ZERO:
                        self.contra_account = self.party.account_receivable.id
                    else:
                        self.contra_account = self.party.account_payable.id
        if self.invoice:
            if self.party != self.invoice.party:
                self.invoice = None
                self.reference = None
                self.contra_account = None
            elif not self.party:
                self.invoice = None
                self.reference = None
            else:
                self.contra_account = self.invoice.account.id

    @fields.depends('date', 'fiscalyear', 'journal', 'account',
        'contra_account')
    def on_change_date(self):
        pool = Pool()
        Fiscalyear = pool.get('account.fiscalyear')
        Period = pool.get('account.period')
        Date = pool.get('ir.date')
        today = Date.today()

        date = self.date or today
        company_id = Transaction().context.get('company', False)
        if not company_id:
            return
        fiscalyear_for_date = Fiscalyear.find(company_id, date=date,
            exception=True)
        fiscalyear_id = self.fiscalyear.id if self.fiscalyear else None
        # check if date relates to different fiscalyear
        if (fiscalyear_for_date != fiscalyear_id
                and self.journal):
            self.fiscalyear = fiscalyear_for_date
            self.account = self.batch.journal.account
            self.contra_account = None
        # check if date is valid for the period/fiscalyear
        if Transaction().context.get('period'):
            period = Period(Transaction().context['period'])
            period_for_date = period.find(company_id, date=date,
                exception=False, test_state=True)
            if period_for_date != period.id:
                self.date = None
        elif Transaction().context.get('fiscalyear'):
            if fiscalyear_for_date != Transaction().context['fiscalyear']:
                self.date = None

    @fields.depends('invoice', 'date', 'batch', 'amount', 'journal')
    def on_change_invoice(self):
        pool = Pool()
        Currency = pool.get('currency.currency')
        BatchJournal = pool.get('account.batch.journal')

        journal = self.journal or self.batch and self.batch.journal
        if not journal:
            journal_id = Transaction().context.get('journal')
            journal = BatchJournal(journal_id)

        if self.invoice:
            self.is_cancelation_move = None
            if self.invoice.type == 'out':
                sign = 1
                reference = self.invoice.number
            else:
                sign = -1
                reference = self.invoice.reference or self.invoice.number
            with Transaction().set_context(date=self.invoice.currency_date):
                amount_to_pay = sign * (Currency.compute(self.invoice.currency,
                    self.invoice.amount_to_pay, journal.currency))
            if not self.amount or abs(self.amount) > abs(amount_to_pay):
                self.amount = amount_to_pay
            self.party = self.invoice.party.id
            self.contra_account = self.invoice.account.id
            self.reference = reference
        else:
            self.reference = None

    @classmethod
    def get_function_fields(cls, lines, names):
        res = {}
        # preset empty values for side*_account
        ids = [l.id for l in lines]
        defaults = {}.fromkeys(ids, '')
        for name in names:
            if name in ['side_account', 'side_contra_account']:
                res[name] = defaults.copy()
                continue
            res[name] = {}
        for line in lines:
            line_id = line.id
            amount = line.amount or _ZERO
            journal = line.journal
            account_journal = journal.account_journal
            side = cls._choose_side(amount, account_journal)
            if 'side_account' in names:
                res['side_account'][line_id] = side
            if 'side_contra_account' in names:
                res['side_contra_account'][line_id] = cls._opposite(side)
            if 'currency_digits' in names:
                res['currency_digits'][line_id] = journal.currency.digits
            if 'journal_type' in names:
                res['journal_type'][line_id] = account_journal.type
            if 'state' in names:
                res['state'][line_id] = (line.move.state if line.move
                    else 'staging')
        return res

    @classmethod
    def search_state(cls, name, clause):
        return [('move.state', clause[1], clause[2])]

    @classmethod
    def post(cls, lines):
        pool = Pool()
        Move = pool.get('account.move')
        MoveLine = pool.get('account.move.line')

        Move.post([l.move for l in lines
                if l.move and l.state == 'draft'])

        # Insert order is on top, we reverse to process from first to last
        # (important for invoice reconciling below). We can not use the state
        # of the batch line, because we want to post all moves in one go.
        lines.reverse()
        for line in [l for l in lines if l.invoice
                and l.invoice.state not in ('cancel', 'paid')]:
            amount_to_pay = line.invoice.amount_to_pay
            for move_line in line.move.lines:
                if move_line.account == line.invoice.account:
                    break
            if amount_to_pay == _ZERO:
                # Don't reconcile here, if a later batch line
                # refers to the same invoice
                reconcile = True
                invoice_batch_lines = cls.search([
                    ('invoice', '=', line.invoice.id),
                    ('id', '!=', line.id),
                    ])
                if invoice_batch_lines:
                    for iline in invoice_batch_lines:
                        if iline.id > line.id:
                            reconcile = False
                            break
                if reconcile:
                    reconcile_lines, remainder = \
                        line.invoice.get_reconcile_lines_for_amount(_ZERO)
                    if remainder == _ZERO and move_line in reconcile_lines:
                        MoveLine.reconcile(reconcile_lines)

    @classmethod
    def check_unposted_batch_lines_for_account(cls, account_ids=None):
        if not account_ids:
            return False
        account_ids = list(set(account_ids))
        lines = cls.search(
                ['AND', ['OR', ('account', 'in', account_ids),
                    ('contra_account', 'in', account_ids),
                    ],
                    ('state', '!=', 'posted'),
                    ('journal.account_journal.type', '!=', 'situation'),])
        return lines

    def set_code(self):
        Sequence = Pool().get('ir.sequence')

        if not self.code:
            self.write([self], {
                    'code': Sequence.get('account.batch.line'),
                    })

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')

        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            if not vals.get('sequence'):
                vals['sequence'] = Sequence.get('account.batch.line.create')
        lines = super(BatchLine, cls).create(vlist)
        for line in lines:
            line.create_move()
            if line.invoice:
                line._add_payment_line()
                # This check must be run *after* payment lines are added to
                # have all the payment lines available
                line._check_invoice_amount()
        return lines

    def create_move(self):
        '''
        Create one move per line and try to reconcile the lines.
        Returns the move
        '''
        key = {'date': self.date}
        move = self._get_move(key)
        move.lines = self.get_move_lines()
        move.save()

        self.write([self], {
                'move': move.id,
                })
        return move

    def _get_move(self, key):
        'Return a Move for the key'
        pool = Pool()
        Move = pool.get('account.move')
        Period = pool.get('account.period')

        company = (self.batch.company if self.batch else
            Transaction().context.get('company'))
        period_id = Period.find(company, date=key['date'])
        return Move(
            period=period_id,
            journal=self.journal.account_journal,
            date=key['date'],
            origin=self,
            company=company,
            description=self.posting_text,
            reference=self.reference,
            )

    def get_move_lines(self):
        '''
        Return the move lines for the batch line move
        '''
        pool = Pool()
        Currency = pool.get('currency.currency')
        Company = pool.get('company.company')

        res = []
        company = (self.batch.company if self.batch else
            Transaction().context.get('company'))
        if isinstance(company, int):
            company = Company(company)
        journal = self.journal
        with Transaction().set_context(date=self.date):
            amount = Currency.compute(journal.currency,
                self.amount, company.currency)
        if journal.currency != company.currency:
            second_currency = journal.currency.id
            amount_second_currency = abs(self.amount)
        else:
            amount_second_currency = None
            second_currency = None
        side = self.__class__._choose_side(
            amount, journal.account_journal)
        if side == 'credit':
            debit_account = self.contra_account
            credit_account = self.account
        elif side == 'debit':
            debit_account = self.account
            credit_account = self.contra_account

        cancel = self.is_cancelation_move

        if self.tax:
            taxes = self._get_taxes(self.tax)
            base_tax_lines = []
            for tax in taxes:
                total_amount = base_amount = amount
                if not self.tax.reverse_charge:
                    base_amount = tax.reverse_compute(amount, taxes)
                if tax.type == 'percentage':
                    tax_amount = base_amount * tax.rate
                elif tax.type == 'fixed':
                    tax_amount = tax.amount
                currency = journal.currency
                base_amount = currency.round(base_amount)
                tax_amount = currency.round(tax_amount)
                # Create the move line(s) for the taxes
                # XXX: Unhandled case: tax_amount_second_currency
                tax_amount_second_currency = None
                abs_tax_amount = abs(tax_amount)
                abs_base_amount = abs(base_amount)
                abs_total_amount = abs(total_amount)
                tax_credit_account = tax.invoice_account
                tax_debit_account = tax.credit_note_account
                if not cancel:
                    if side == 'credit':
                        tax_move_line = self._get_move_line(
                            abs_tax_amount, _ZERO,
                            tax_credit_account, second_currency,
                            tax_amount_second_currency)
                    elif side == 'debit':
                        tax_move_line = self._get_move_line(
                            _ZERO, abs_tax_amount,
                            tax_debit_account, second_currency,
                            tax_amount_second_currency)
                elif cancel:
                    abs_tax_amount = -abs_tax_amount
                    abs_base_amount = -abs_base_amount
                    abs_total_amount = -abs_total_amount
                    if side == 'debit':
                        tax_move_line = self._get_move_line(
                            abs_tax_amount, _ZERO,
                            tax_debit_account, second_currency,
                            tax_amount_second_currency)
                    elif side == 'credit':
                        tax_move_line = self._get_move_line(
                            _ZERO, abs_tax_amount,
                            tax_credit_account, second_currency,
                            tax_amount_second_currency)
                # Create the tax line(s) for the tax(es)
                def get_tax_group(tax):
                    tax_group = tax.group
                    if not tax_group and tax.parent:
                        tax_group = get_tax_group(tax.parent)
                    return tax_group

                tax_group = get_tax_group(tax)
                tax_group_kind = tax_group.kind if tax_group else None
                if ((tax_group_kind is None
                    or (tax_group_kind in ['sale', 'both'])
                    and ((self.amount >= 0 and not cancel)
                        or (self.amount < 0 and cancel)
                                ))):
                    #print('normal', tax_group_kind)
                    base_tax_amount = abs_base_amount
                else:
                    #print('reverse', tax_group_kind)
                    abs_tax_amount *= -1
                    base_tax_amount = -abs_base_amount

                tax_line = self._get_tax_line(abs_tax_amount, 'tax', tax)
                tax_move_line.tax_lines += (tax_line,)
                # Create the tax line(s) for the base
                base_tax_line = self._get_tax_line(base_tax_amount,
                    'base', tax)
                base_tax_lines.append(base_tax_line)
                res.append(tax_move_line)

            # Create the move line(s) for the base and total
            if not cancel:
                if side == 'credit':
                    base_move_line = self._get_move_line(
                        abs_base_amount, _ZERO,
                        debit_account, second_currency, amount_second_currency)
                    total_move_line = self._get_move_line(
                        _ZERO, abs_total_amount, credit_account,
                        second_currency, amount_second_currency)
                elif side == 'debit':
                    base_move_line = self._get_move_line(
                        _ZERO, abs_base_amount, credit_account,
                        second_currency, amount_second_currency)
                    total_move_line = self._get_move_line(
                        abs_total_amount, _ZERO,
                        debit_account, second_currency, amount_second_currency)
            elif cancel:
                if side == 'debit':
                    base_move_line = self._get_move_line(
                        abs_base_amount, _ZERO, credit_account,
                        second_currency, amount_second_currency)
                    total_move_line = self._get_move_line(
                        _ZERO, abs_total_amount,
                        debit_account, second_currency, amount_second_currency)
                elif side == 'credit':
                    base_move_line = self._get_move_line(
                        _ZERO, abs_base_amount,
                        debit_account, second_currency, amount_second_currency)
                    total_move_line = self._get_move_line(
                        abs_total_amount, _ZERO, credit_account,
                        second_currency, amount_second_currency)
            # add the previously created tax lines to the base
            base_move_line.tax_lines = base_tax_lines
            res.extend([base_move_line, total_move_line])

        else:
            amount = abs(amount)
            if not cancel:
                res.append(self._get_move_line(_ZERO, amount, credit_account,
                        second_currency, amount_second_currency))
                res.append(self._get_move_line(amount, _ZERO, debit_account,
                        second_currency, amount_second_currency))
            else:
                amount = -amount
                if amount_second_currency:
                    amount_second_currency = -amount_second_currency
                res.append(self._get_move_line(amount, _ZERO, credit_account,
                        second_currency, amount_second_currency))
                res.append(self._get_move_line(_ZERO, amount, debit_account,
                        second_currency, amount_second_currency))
        return res

    def _get_move_line(self, debit, credit, account, second_currency,
            amount_second_currency):
        pool = Pool()
        MoveLine = pool.get('account.move.line')

        return MoveLine(
            description=self.posting_text,
            debit=debit,
            credit=credit,
            account=account,
            party=self.party, # if self.account.party_required else None,
            second_currency=second_currency,
            amount_second_currency=amount_second_currency,
            maturity_date=self.maturity_date,
            code=self.sequence,
            reference=self.reference or '',
            tax_lines=[],
            )

    def _get_taxes(self, tax):
        res = []
        if tax.type != 'none':
            res.append(tax)
        if tax.childs:
            for child in tax.childs:
                res.extend(self._get_taxes(child))
        return res

    def _get_tax_line(self, amount, line_type, tax):
        pool = Pool()
        TaxLine = pool.get('account.tax.line')

        vat_code = None
        if tax.vat_code_required:
            if not self.party or not self.party.vat_code:
                raise UserError(gettext(
                        'account_batch.missing_vat_code'))
            vat_code = self.party.vat_code

        return TaxLine(
            amount=amount,
            type=line_type,
            tax=tax.id,
            vat_code=vat_code,
            )

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        args = []

        lines_to_update = set()
        for lines, values in zip(actions, actions):
            if cls._check_update_move(set(values.keys())):
                args.extend((lines, values))
                lines_to_update.update(set(lines))
        if lines_to_update:
            super(BatchLine, cls).write(*args)
            for line in lines_to_update:
                if line.move:
                    line._update_move_lines()
                    if line.invoice:
                        line._add_payment_line()
                        # This check must be run *after* payment lines
                        # are added to have all payment lines available
                        line._check_invoice_amount()

    @classmethod
    def _check_update_move(cls, fields):
        if fields.difference(cls._check_modify_exclude):
            return True
        return False

    def _update_move_lines(self):
        pool = Pool()
        Move = pool.get('account.move')
        MoveLine = pool.get('account.move.line')
        Reconciliation = pool.get('account.move.reconciliation')

        # Remove evtl. reconciliaton when rewriting the move lines:
        # Rewriting should only happen in state draft, so reconciliation will
        # be made again when posting the line. Usually it should not be
        # possible at all to use any reconciliated item on draft lines. (#2905)
        reconciliations = [
            l.reconciliation for l in self.move.lines if l.reconciliation]
        if reconciliations:
            Reconciliation.delete(reconciliations)

        # Delete former move lines and re-create new
        MoveLine.delete(self.move.lines)
        move = Move(self.move.id)
        move.lines = self.get_move_lines()
        move.save()

    def _add_payment_line(self):
        Invoice = Pool().get('account.invoice')
        for move_line in self.move.lines:
            if move_line.account == self.invoice.account:
                Invoice.write([self.invoice], {
                        'payment_lines': [('add', [move_line.id])],
                        })
                break

    def _unreconcile_and_remove_payment_line(self):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Reconciliation = pool.get('account.move.reconciliation')

        reconciliations = [
            l.reconciliation for l in self.move.lines if l.reconciliation]
        if reconciliations:
            Reconciliation.delete(reconciliations)
        for move_line in self.move.lines:
            if move_line.account == self.invoice.account:
                Invoice.write([self.invoice], {
                        'payment_lines': [('remove', [move_line.id])],
                        })
                break

    def _check_invoice_amount(self):
        pool = Pool()
        Currency = pool.get('currency.currency')
        Lang = pool.get('ir.lang')

        amount_payable = self._get_amount_payable()
        with Transaction().set_context(date=self.invoice.currency_date):
            amount_payable = Currency.compute(self.invoice.currency,
                amount_payable, self.journal.currency)

        if amount_payable < _ZERO:
            lang, = Lang.search([
                        ('code', '=', Transaction().language),
                    ], limit=1)
            amount = Lang.format(lang,
                    '%.' + str(self.journal.currency.digits) + 'f',
                    self.amount, True)
            amount_payable = Lang.format(lang,
                    '%.' + str(self.journal.currency.digits) + 'f',
                    amount_payable, True)
            raise UserError(gettext(
                    'account_batch.amount_greater_invoice_amount_to_pay',
                    amount, self.invoice.number, self.sequence,
                    amount_payable))

    def _get_amount_payable(self):
        pool = Pool()
        Currency = pool.get('currency.currency')

        if self.invoice.state != 'posted':
            return _ZERO
        amount = _ZERO
        amount_currency = _ZERO
        for line in self.invoice.lines_to_pay:
            if line.second_currency == self.invoice.currency:
                if line.debit - line.credit > _ZERO:
                    amount_currency += abs(line.amount_second_currency)
                else:
                    amount_currency -= abs(line.amount_second_currency)
            else:
                amount += line.debit - line.credit
        for line in self.invoice.payment_lines:
            if line.second_currency == self.invoice.currency:
                if line.debit - line.credit > _ZERO:
                    amount_currency += abs(line.amount_second_currency)
                else:
                    amount_currency -= abs(line.amount_second_currency)
            else:
                amount += line.debit - line.credit
        if self.invoice.type == 'in':
            amount = -amount
            amount_currency = -amount_currency
        if amount != _ZERO:
            with Transaction().set_context(date=self.invoice.currency_date):
                amount_currency += Currency.compute(
                    self.invoice.company.currency, amount,
                    self.invoice.currency)
        return amount_currency

    @classmethod
    def copy(cls, lines, default=None):
        Date = Pool().get('ir.date')

        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('move', None)
        default.setdefault('code', None)
        default.setdefault('sequence', None)
        default.setdefault('invoice', None)
        default.setdefault('date', Date.today())
        return super(BatchLine, cls).copy(lines, default=default)

    @classmethod
    def delete(cls, lines):
        Move = Pool().get('account.move')

        moves = [l.move for l in lines]
        if moves:
            Move.delete(moves)
        super(BatchLine, cls).delete(lines)


class OpenBatchJournalAsk(ModelView):
    'Open Batch Journal Ask'
    __name__ = 'account.batch.open_batch_journal.ask'

    batch_journal = fields.Many2One('account.batch.journal',
        'Batch Journal', required=True, states={
            'readonly': Bool(Eval('batch')),
            }, depends=['batch'])
    batch = fields.Many2One('account.batch', 'Batch', domain=[
            ('journal', If(Bool(Eval('batch_journal')), '=', '!='),
                Eval('batch_journal')),
            ('state', '=', 'open'),
            ], depends=['batch_journal'])
    show_draft = fields.Boolean('Show Draft')
    show_posted = fields.Boolean('Show Posted')
    period = fields.Many2One('account.period', 'Period', domain=[
            ('fiscalyear', If(Bool(Eval('fiscalyear')), '=', '!='),
                Eval('fiscalyear'))
            ], depends=['fiscalyear'])
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscalyear')
    company = fields.Many2One('company.company', 'Company', required=True,
            domain=[('company', '=', Get(Eval('context', {}), 'company',
                False))])

    @staticmethod
    def default_show_draft():
        return True

    @staticmethod
    def default_show_posted():
        return False

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @fields.depends('batch')
    def on_change_with_batch_journal(self, name=None):
        if self.batch:
            return self.batch.journal.id
        return False

    def on_change_fiscalyear(self):
        self.period = None

    @fields.depends('period')
    def on_change_period(self):
        self.fiscalyear = None
        if self.period:
            self.fiscalyear = self.period.fiscalyear.id


class OpenBatchJournal(Wizard):
    'Open Batch Journal'
    __name__ = 'account.batch.open_batch_journal'
    start = StateTransition()
    ask = StateView('account.batch.open_batch_journal.ask',
        'account_batch.open_batch_journal_ask_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('account_batch.act_batch_line_form_editable')

    def transition_start(self):
        #if (Transaction().context.get('active_model', '')
        #        == 'account.journal.period'
        #        and Transaction().context.get('active_id')):
        #    return 'open_'
        return 'ask'

    def do_open_(self, action):
        batch_journal = self.ask.batch_journal
        batch = self.ask.batch
        fiscalyear = self.ask.fiscalyear
        period = self.ask.period

        # Use name from view_header_get
        del action['name']
        del action['rec_name']

        domain = []
        ctx = {}
        domain.append(('journal', '=', batch_journal.id))
        ctx['journal'] = batch_journal.id

        _move_states = []
        if self.ask.show_draft:
            _move_states.append('draft')
        if self.ask.show_posted:
            _move_states.append('posted')
            ctx['posted'] = self.ask.show_posted
        domain.append(('move.state', 'in', _move_states))

        if batch:
            domain.append(('batch', '=', self.ask.batch.id))
            ctx['batch'] = batch.id

        if period:
            domain.append(('move.period.id', '=', period.id))
            ctx['period'] = period.id

        if fiscalyear:
            domain.append(('fiscalyear.id', '=', fiscalyear.id))
            ctx['fiscalyear'] = fiscalyear.id

        if not action.get('name'):
            action['name'] = ''
        header_suffix = ''
        if self.ask.show_posted:
            header_suffix += ' (*)'
        ctx['header_suffix'] = header_suffix

        action['pyson_domain'] = PYSONEncoder().encode(domain)
        action['pyson_context'] = PYSONEncoder().encode(ctx)

        return action, {}

    def transition_open_(self):
        return 'end'


class PostBatchLines(Wizard):
    'Post Batch Lines'
    __name__ = 'account.batch.post'
    start_state = 'post'
    post = StateTransition()

    def transition_post(self):
        pool = Pool()
        BatchLine = pool.get('account.batch.line')

        lines = BatchLine.browse(Transaction().context['active_ids'])
        BatchLine.post(lines)
        return 'end'


class CancelBatchLinesAskSure(ModelView):
    'Cancel Batch Lines Ask Sure'
    __name__ = 'account.batch.cancel.ask.sure'


class CancelBatchLinesAskProblem(ModelView):
    'Cancel Batch Lines Ask Problem'
    __name__ = 'account.batch.cancel.ask.problem'


class CancelBatchLines(Wizard):
    'Cancel Batch Lines'
    __name__ = 'account.batch.cancel'
    start = StateTransition()
    ask_draft = StateView('account.batch.cancel.ask.problem',
        'account_batch.wiz_cancel_batch_lines_ask_problem_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'confirm', 'tryton-ok', default=True),
            ])
    confirm = StateView('account.batch.cancel.ask.sure',
        'account_batch.wiz_cancel_batch_lines_ask_sure_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'cancelation', 'tryton-ok', default=True),
            ])
    cancelation = StateTransition()

    def transition_start(self):
        BatchLine = Pool().get('account.batch.line')
        draft_lines = [l for l in
            BatchLine.browse(Transaction().context['active_ids'])
            if l.state != 'posted']
        if draft_lines:
            return 'ask_draft'
        return 'confirm'

    def transition_cancelation(self):
        self._process_cancelation()
        return 'end'

    def _process_cancelation(self):
        BatchLine = Pool().get('account.batch.line')

        lines_to_cancel = [l for l in
            BatchLine.browse(Transaction().context['active_ids'])
            if l.state == 'posted']
        to_create = []
        for line in lines_to_cancel:
            to_create.append(self._get_cancelation_values(line))
            if line.invoice:
                line._unreconcile_and_remove_payment_line()
        if to_create:
            lines = BatchLine.create(to_create)
            BatchLine.post(lines)

    def _get_cancelation_values(self, batch_line):
        pool = Pool()
        Period = pool.get('account.period')
        Fiscalyear = pool.get('account.fiscalyear')

        company_id = Transaction().context['company']
        cancelation = gettext('account_batch.msg_cancelation')
        posting_text = '%s: %s' % (cancelation, batch_line.code)
        if batch_line.posting_text:
            posting_text += ' (%s)' % (batch_line.posting_text,)
        reference = None
        if batch_line.reference:
            reference = '%s: %s' % (cancelation, batch_line.reference)

        posting_date = batch_line.date
        if batch_line.fiscalyear:
            fiscalyear = batch_line.fiscalyear
        else:
            fiscalyear_id = Fiscalyear.find(
                company_id, date=batch_line.date, exception=True)
            fiscalyear = Fiscalyear(fiscalyear_id)
        clause = [
            ('start_date', '<=', posting_date),
            ('end_date', '>=', posting_date),
            ('fiscalyear.company', '=', company_id),
            ('fiscalyear', '=', fiscalyear.id),
            ('type', '=', 'standard'),
            ('state', '!=', 'close'),
            ]
        periods = Period.search(clause, order=[('start_date', 'ASC')],
            limit=1)
        if not periods:
            clause = ['OR',
                [
                    ('start_date', '<=', posting_date),
                    ('end_date', '>=', posting_date),
                    ('fiscalyear.company', '=', company_id),
                    ('fiscalyear', '=', fiscalyear.id),
                    ('state', '!=', 'close'),
                    ],
                [
                    ('start_date', '>', posting_date),
                    ('fiscalyear.company', '=', company_id),
                    ('fiscalyear', '=', fiscalyear.id),
                    ('state', '!=', 'close'),
                    ]
                ]
            periods = Period.search(clause, order=[
                ('start_date', 'ASC')], limit=1)
            if not periods:
                raise UserError(gettext(
                        'account.batch.no_period_fiscalyear',
                        fiscalyear.name))
            period = periods[0]
            if posting_date < period.start_date:
                posting_date = period.start_date

        return {
            'batch': batch_line.batch,
            'account': batch_line.account,
            'contra_account': batch_line.contra_account,
            'amount': batch_line.amount * -1,
            'tax': batch_line.tax,
            'is_cancelation_move': not bool(batch_line.is_cancelation_move),
            'journal': batch_line.journal,
            'date': posting_date,
            'reference': reference,
            'posting_text': posting_text,
            'party': batch_line.party,
            'fiscalyear': fiscalyear,
            }
