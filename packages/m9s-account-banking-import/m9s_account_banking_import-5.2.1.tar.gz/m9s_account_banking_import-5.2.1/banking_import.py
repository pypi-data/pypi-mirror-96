# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import datetime

from decimal import Decimal
from sql import Null

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import (Wizard, StateView, StateAction, StateTransition,
    Button)
from trytond.pyson import If, Equal, Eval, Not, Bool, PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.config import config as config_
from trytond.exceptions import UserError, UserWarning
from trytond.i18n import gettext

amount_digits = (16, config_.getint('account_banking_import', 'amount_digits',
        default=2))

_ZERO = Decimal("0.0")
_STATES = {'readonly': Bool(Eval('lines'))}
_DEPENDS = ['lines']
_STATESF = {'readonly': Not(Equal(Eval('state'), 'draft'))}
_DEPENDSF = ['state']


class BankingImportConfiguration(ModelSQL, ModelView):
    'Bank Import Configuration'
    __name__ = 'banking.import.configuration'

    name = fields.Char('Name', required=True, translate=True)
    company = fields.Many2One('company.company', 'Company', required=True,
        select=True, states=_STATES, domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        depends=_DEPENDS)
    bank_account = fields.Many2One('bank.account', 'Bank Account',
        required=True, states=_STATES, depends=_DEPENDS,
        #domain=[('owners', 'in', company)],
        help='Bank Account of the company, for which the transactions '
        'will be imported.')
    journal = fields.Many2One('account.batch.journal', 'Batch Journal',
        required=True, states=_STATES, depends=_DEPENDS,
        domain=[('account_journal.type', '=', 'bank')],
        help='Bank Journal used for this import configuration.')
    import_method = fields.Selection([], 'Import Method', sort=True,
        required=True, states=_STATES, depends=_DEPENDS,
        help='Import Method to use for this configuration.\n'
        '(Import Methods are provided by specific Submodules)')
    entry_date = fields.Selection([
            ('date', 'Date'),
            ('vdate', 'Valuta Date'),
            ], 'Entry date', sort=True,
        help='The date of the bank statement, '
        'that shall be used as entry date for accounting.')
    active = fields.Boolean('Active')
    lines = fields.One2Many('banking.import.line', 'bank_import_config',
        'Imported Transactions', readonly=True)
    processing_start_date = fields.Date('Processing Start Date',
        help='The date from which on transactions shall be presented '
        'for processing.')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_bank_account():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            if len(company.party.bank_accounts) == 1:
                return company.party.bank_accounts[0].id

    @staticmethod
    def default_entry_date():
        return 'date'

    @staticmethod
    def default_active():
        return True

    @classmethod
    def validate(cls, configurations):
        cls._sanity_checks(configurations)

    @classmethod
    def _sanity_checks(cls, configurations):
        for configuration in configurations:
            configurations = cls.search([
                    ('bank_account', '=', configuration.bank_account),
                    ('active', '=', True),
                    ])
            if len(configurations) > 1:
                raise UserError(gettext(
                        'account_banking_import.msg_bank_account_used'))
            configurations = cls.search([
                    ('journal.account_journal', '=',
                        configuration.journal.account_journal),
                    ('active', '=', True),
                    ])
            if len(configurations) > 1:
                raise UserError(gettext(
                        'account_banking_import.msg_journal_used'))
                return False
            if not configuration.bank_account.currency:
                raise UserError(gettext(
                        'account_banking_import.msg_missing_currency_account'))
            if (configuration.bank_account.currency !=
                    configuration.journal.currency):
                raise UserError(gettext(
                        'account_banking_import.msg_wrong_currency'))

    @classmethod
    def get_transactions(cls, configurations):
        for configuration in configurations:
            method_name = 'get_transactions_%s' % configuration.import_method
            if not hasattr(configuration, method_name):
                raise UserError(gettext(
                        'account_banking_import.msg_method_not_available',
                        configuration.import_method))
            getattr(configuration, method_name)()

    def _get_batch(self):
        '''
        Return values for a batch to insert banking import lines

        :returns: - None if there are unposted batch lines
                  - the batch in case of success
        '''
        pool = Pool()
        Batch = pool.get('account.batch')
        BatchLine = pool.get('account.batch.line')
        Lang = pool.get('ir.lang')

        if not self.journal.account:
            raise UserError(gettext(
                    'account_banking_import.missing_journal_account'))

        # for correct start balance check there may be no unposted
        # batch lines for same accounts
        account_ids = [self.journal.account.id]
        batch_lines = BatchLine.check_unposted_batch_lines_for_account(
            account_ids)
        if batch_lines:
            msg = '\n\n'
            msg += '\n'.join([l.rec_name for l in batch_lines])
            raise UserError(gettext(
                    'account_banking_import.msg_unposted_batch_lines',
                    batch_lines=msg))

        lang, = Lang.search([
                    ('code', '=', Transaction().language),
                ], limit=1)
        now = datetime.datetime.now().strftime(str(lang.date) + " %H:%M")
        batch = Batch(
            name='Bank Import ' + self.name + ' (' + now + ')',
            journal=self.journal,
            )
        batch.save()
        return batch

    def _clean_warnings(self):
        '''
        Clean the user warnings of the last run, they shall only persist for one
        wizard session.
        '''
        pool = Pool()
        Warning = pool.get('res.user.warning')
        warnings = Warning.search([
                ('user', '=', Transaction().user),
                ('name', 'like', 'Banking Import:%'),
                ])
        if warnings:
            Warning.delete(warnings)


class BankingImportLine(ModelSQL, ModelView):
    'Bank Import Line'
    __name__ = 'banking.import.line'

    bank_import_config = fields.Many2One('banking.import.configuration',
            'Bank Import Configuration', required=True, ondelete='RESTRICT',
            readonly=True)
    date = fields.Date('Date', required=True, readonly=True)
    valuta_date = fields.Date('Valuta Date', required=True, readonly=True)
    contra_name = fields.Char('Contra Account Name', readonly=True,
            help='Name of the owner of the Contra Account')
    contra_account = fields.Char('Contra Account Number', readonly=True,
            help='Number of the Contra Account')
    contra_bank_code = fields.Char('Contra Account Bank Code', readonly=True,
            help='Bank/Business Identifier Code of the Contra Account')
    amount = fields.Numeric('Amount', digits=amount_digits, required=True,
            readonly=True)
    purpose = fields.Text('Purpose', readonly=True)
    balance = fields.Numeric('Balance', digits=amount_digits,
            required=True, readonly=True,
            help='New balance at the end of the transaction')
    kind = fields.Char('Kind', readonly=True)
    customer_ref = fields.Char('Customer Reference', readonly=True)
    code = fields.Char('Code', readonly=True)
    addkey = fields.Char('Additional Key', readonly=True)
    primanota = fields.Char('Primanota', readonly=True)

    def get_rec_name(self, name):
        pool = Pool()
        Lang = pool.get('ir.lang')

        lang, = Lang.search([
                    ('code', '=', Transaction().language),
                ], limit=1)
        entry_date = self._get_entry_date()
        return '%s, %s, %s, %s' % (entry_date.strftime(str(lang.date)),
                self.contra_name, self.contra_account, self.contra_bank_code)

    @classmethod
    def search_rec__name__(cls, name, clause):
        return ['OR',
            ('contra_name',) + tuple(clause[1:]),
            ('contra_account',) + tuple(clause[1:]),
            ('contra_bank_code',) + tuple(clause[1:]),
            ]

    def _get_entry_date(self):
        if self.bank_import_config.entry_date == 'date':
            return self.date
        else:
            return self.valuta_date

    def match_invoice(self):
        '''
        Find matching invoices for the import line.

        Extend in submodules to suit specific needs, number formats, etc.

        Note:
        The more unique invoice numbers are the better will be the match result.
        This simple matcher will produce many false positives in a tryton
        default configuration.

        :returns: a list of invoices
        '''
        Invoice = Pool().get('account.invoice')

        invoices = []
        if self.purpose:
            purpose = self.purpose.replace('\n','')
            open_invoices = Invoice.search([
                ('state', '=', 'posted'),
                ], order=[('id', 'ASC')])
            for invoice in open_invoices:
                if purpose.find(invoice.number) > -1:
                    invoices.append(invoice)
            #invoice_ids.sort()
        return invoices

    def assess_invoice(self, invoices=None):
        '''
        Make plausibility checks for a specified invoice and return, whether
        the wizard should present the line for verifying the invoice.

        Extend in submodules to suit specific needs, number formats, etc.

        This example contains one plausibility check:
        - amount of the line must be equal to the total amount to pay of
          all matched invoices

        :param invoices: a list of invoices

        :returns: a dict with
            keys: the invoice_ids
            values: amount_to_pay
                    ask as Boolean (True for ask)
        '''
        pool = Pool()
        Currency = pool.get('currency.currency')

        res = {}
        if invoices is None:
            return res
        plty = 0
        journal = self.bank_import_config.journal
        invoice_sum = _ZERO
        for invoice in invoices:
            with Transaction().set_context(date=invoice.currency_date):
                amount_to_pay = Currency.compute(invoice.currency,
                        invoice.amount_to_pay, journal.currency)
            res.setdefault(invoice.id, {})
            res[invoice.id]['amount_to_pay'] = amount_to_pay
            invoice_sum += amount_to_pay
        if invoice_sum == self.amount:
            plty += 1
        for invoice in invoices:
            if plty > 0:
                res[invoice.id]['ask'] = False
            else:
                res[invoice.id]['ask'] = True
        return res

    def create_batch_line(self, batch, journal, invoice):
        pool = Pool()
        BatchLine = pool.get('account.batch.line')

        line = BatchLine(batch=batch, journal=journal, invoice=invoice,
            date=self._get_entry_date(), bank_imp_line=self.id)
        line.on_change_invoice()
        return line


class RunImportStart(ModelView):
    'Run Import Start'
    __name__ = 'banking.run_import.start'
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ])
    employee = fields.Many2One('company.employee', 'Employee', required=True,
        domain=[
            ('company', '=', Eval('company')),
            ], depends=['company'])
    bank_import_config = fields.Many2One('banking.import.configuration',
            'Bank Import Configuration', required=True, ondelete='RESTRICT',
            help='Bank Import Configuration to use for this run')
    update_transactions = fields.Boolean('Update Transactions',
        help='Whether the transactions of the selected account shall be '
        'updated before running the import into a batch journal')
    # Helper fields defined here to be available during the whole
    # session, to be filled/used in later steps
    batch = fields.Many2One('account.batch', 'Batch')
    journal = fields.Many2One('account.batch.journal', 'Batch Journal')
    counter_total = fields.Integer('Counter Total')
    start_balance = fields.Numeric('Start Balance', digits=amount_digits,
            help='Start balance at the begin of the import')
    running_balance = fields.Numeric('Running Balance', digits=amount_digits,
            help='Balance updated with each imported line')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_employee():
        User = Pool().get('res.user')

        employee_id = None
        if Transaction().context.get('employee'):
            employee_id = Transaction().context['employee']
        else:
            user = User(Transaction().user)
            if user.employee:
                employee_id = user.employee.id
        return employee_id

    @staticmethod
    def default_bank_import_config():
        BankConfig = Pool().get('banking.import.configuration')

        configs = BankConfig.search([])
        if len(configs) == 1:
            return configs[0].id

    @staticmethod
    def default_update_transactions():
        return True


class RunImportShow(ModelView):
    'Run Import Show'
    __name__ = 'banking.run_import.show'
    bank_import_config = fields.Many2One('banking.import.configuration',
        'Bank Import Configuration')
    batch = fields.Many2One('account.batch', 'Batch')
    journal = fields.Many2One('account.batch.journal', 'Batch Journal')
    counter = fields.Char('Counter', readonly=True,
        help='Display of the actual and total number of banking import lines')
    lines = fields.Many2Many('banking.import.line', None, None, 'Unprocessed Lines',
        readonly=True)
    line = fields.Many2One('banking.import.line', 'Banking Import Line',
        readonly=True)
    date = fields.Date('Date', required=True, readonly=True)
    valuta_date = fields.Date('Valuta Date', required=True, readonly=True)
    contra_name = fields.Char('Contra Account Name', readonly=True,
        help='Name of the owner of the Contra Account')
    contra_account = fields.Char('Contra Account Number', readonly=True,
        help='Number of the Contra Account')
    contra_bank_code = fields.Char('Contra Account Bank Code', readonly=True,
        help='Bank/Business Identifier Code of the Contra Account')
    amount = fields.Numeric('Amount', digits=amount_digits, required=True,
        readonly=True)
    purpose = fields.Text('Purpose', readonly=True)
    balance = fields.Numeric('Balance', digits=amount_digits,
        required=True, readonly=True,
        help='New balance at the end of the transaction')
    kind = fields.Char('Kind', readonly=True)
    customer_ref = fields.Char('Customer Reference', readonly=True)
    code = fields.Char('Code', readonly=True)
    addkey = fields.Char('Additional Key', readonly=True)
    primanota = fields.Char('Primanota', readonly=True)
    sum_lines = fields.Numeric('Sum Lines', digits=amount_digits,
        readonly=True,
        help='This field displays the sum of the actual encoded lines')
    difference = fields.Numeric('Difference', digits=amount_digits,
        readonly=True,
        help='This field displays the difference to the expected balance.')
    batch_lines = fields.One2Many('account.batch.line', None, 'Batch Lines',
        context={
            'batch': Eval('batch'),
            'journal': Eval('journal'),
            })
    invoices = fields.Many2Many('account.invoice', None, None, 'Related Invoices',
        readonly=True)

    @staticmethod
    def default_batch_lines():
        Date = Pool().get('ir.date')
        today = Date.today()
        # just trigger the first run, will be immediately overridden by
        # on_change_batch_lines
        return [{
                'date': today,
                }]

    @fields.depends('batch', 'batch_lines', 'line', 'invoices', 'journal')
    def on_change_batch_lines(self):
        sum_lines = _ZERO
        for line in self.batch_lines:
            sum_lines += line.amount if line.amount else _ZERO
            amount = line.amount if line.amount else self.line.amount
            side = line.__class__._choose_side(
                amount, self.batch.journal.account_journal)
            line.account = self.batch.journal.account
            line.side_account = side
            line.side_contra_account = line.__class__._opposite(side)
            # Only the first update after creation of line
            if not line.amount:
                line.batch = self.batch.id
                line.journal = self.journal.id
                line.date = self.line._get_entry_date()
                if len(self.batch_lines) == 1:
                    line.amount = amount
                else:
                    line.amount = self.difference
                line.bank_imp_line = self.line.id
                if self.invoices:
                    invoices = list(self.invoices)
                    invoice = invoices.pop()
                    self.invoices = invoices
                    line.invoice = invoice.id
                    line.on_change_invoice()
                sum_lines += line.amount
        self.sum_lines = sum_lines
        if self.line:
            self.difference = self.line.amount - sum_lines


class RunImportInfoNoLines(ModelView):
    'Run Import Info No Lines'
    __name__ = 'banking.run_import.info_no_lines'


class RunImport(Wizard):
    'Run Import'
    __name__ = 'banking.run_import'
    start = StateView('banking.run_import.start',
        'account_banking_import.run_import_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Process', 'process_', 'tryton-ok', default=True),
            ])
    process_ = StateTransition()
    info_no_lines = StateView('banking.run_import.info_no_lines',
        'account_banking_import.run_import_info_no_lines_view_form', [
            Button('Ok', 'clean', 'tryton-ok'),
            ])
    next_ = StateTransition()
    show = StateView('banking.run_import.show',
        'account_banking_import.run_import_show_view_form', [
            Button('Cancel', 'open_batch', 'tryton-cancel'),
            Button('Next', 'save_lines', 'tryton-go-next'),
            ])
    save_lines = StateTransition()
    clean = StateTransition()
    open_batch = StateAction('account_batch.act_batch_form')
    open_lines = StateAction('account_batch.act_batch_line_form_editable')

    def transition_clean_(self):
        self.start.bank_import_config._clean_warnings()
        return 'end'

    def transition_process_(self):
        config = self.start.bank_import_config
        batch = config._get_batch()
        self.start.batch = batch
        self.start.journal = batch.journal
        if self.start.update_transactions:
            config.get_transactions([config])
        return 'next_'

    def get_unprocessed_lines(self, config):
        '''
        Return a list of import lines that are not yet processed into
        batch lines.
        - Search all import lines. that are not referenced by any posted
          batch line of the configured journal
        - Exclude amounts of 0, they have no posted move lines
        '''
        pool = Pool()
        BatchLine = pool.get('account.batch.line')
        batch_line = BatchLine.__table__()
        Line = pool.get('banking.import.line')
        line = Line.__table__()
        Configuration = pool.get('banking.import.configuration')
        configuration = Configuration.__table__()
        AccountMove = pool.get('account.move')
        account_move = AccountMove.__table__()
        cursor = Transaction().connection.cursor()

        if config.entry_date == 'date':
            line_date = line.date
        else:
            line_date = line.valuta_date
        start_date = config.processing_start_date or datetime.date.min

        subselect = batch_line.join(account_move,
            condition=batch_line.move == account_move.id
            ).select(batch_line.bank_imp_line,
                where=(batch_line.journal == config.journal.id)
                & (account_move.state == 'posted')
                & (batch_line.bank_imp_line != Null))

        cursor.execute(*line.join(configuration,
                condition=line.bank_import_config == configuration.id
                ).select(line.id,
                where=~(line.id.in_(subselect))
                & (line.amount != _ZERO)
                & (configuration.journal == config.journal.id)
                & (line_date >= start_date),
                order_by=[line_date.desc, line.id.desc]))
        return [id for id, in cursor.fetchall()]

    def transition_next_(self):
        pool = Pool()
        Line = pool.get('banking.import.line')
        Config = pool.get('banking.import.configuration')

        Transaction().context.update({
                'batch': self.start.batch.id,
                'journal': self.start.batch.journal.id,
                })

        def next_line():
            lines = list(self.show.lines)
            if not lines:
                return
            counter_actual = (self.start.counter_total - len(lines)) + 1
            counter = '%s / %s' % (counter_actual, self.start.counter_total)
            Transaction().context.update({
                    'counter': counter,
                    })
            line = lines.pop()
            self.show.line = line
            self.show.lines = lines
            # check the balance of the line against the running balance
            # (i.e. check for wrong balances on lines or skipped lines
            actual_line = Line(line)
            line_balance = actual_line.balance - actual_line.amount
            if line_balance != self.start.running_balance:
                raise UserWarning(
                    'Banking Import: Running balance check',
                    gettext('account_banking_import.msg_wrong_line_balance',
                        line=line.rec_name,
                        line_balance=line_balance,
                        journal_balance=self.start.running_balance,
                        difference=line_balance - self.start.running_balance))
            # invoice matching
            invoices = actual_line.match_invoice()
            invoice_ids = []
            skip_show = False
            if invoices:
                inv2amount = actual_line.assess_invoice(invoices)
                # ask == True: continue with show
                # ask == False: create the according batch line and skip show
                for invoice_id, values in inv2amount.items():
                    if values['ask'] is False:
                        batch_line = actual_line.create_batch_line(
                            self.start.batch.id, self.start.journal.id,
                            invoice_id)
                        batch_line.save()
                        self.start.running_balance += batch_line.amount
                        skip_show = True
                    invoice_ids.append(invoice_id)
            Transaction().context.update({
                'invoices': invoice_ids,
                })
            if skip_show:
                next_line()
            return line

        if getattr(self.show, 'lines', None) is None:
            config = self.start.bank_import_config
            lines_to_process = self.get_unprocessed_lines(config)
            if not lines_to_process:
                return 'info_no_lines'
            start_balance = self.start.batch.get_start_balance()
            self.start.start_balance = start_balance
            self.start.running_balance = start_balance
            self.show.lines = lines_to_process
            self.start.counter_total = len(lines_to_process)

            # Write the future processing_start_date as the first date found
            # -1 day depending on the entry_date configuration
            first_line = Line(lines_to_process[-1])
            future_start_date = (first_line._get_entry_date()
                - datetime.timedelta(days=1))
            start_date = config.processing_start_date or datetime.date.min
            if start_date < future_start_date:
                Config.write([config], {
                        'processing_start_date': future_start_date,
                        })
            # check the balance of the first line against the journal balance
            line_balance = first_line.balance - first_line.amount
            if line_balance != start_balance:
                raise UserWarning(
                    'Banking Import: Initial balance check',
                    gettext('account_banking_import.msg_wrong_initial_balance',
                        line=first_line.rec_name,
                        line_balance=line_balance,
                        journal_balance=start_balance,
                        difference=line_balance - start_balance))

        if not next_line():
            return 'open_batch'
        return 'show'

    def default_show(self, fields):
        defaults = {
            'batch': Transaction().context['batch'],
            'journal': Transaction().context['journal'],
            'bank_import_config': self.start.bank_import_config.id,
            'counter': Transaction().context.get('counter', ''),
            'lines': [a.id for a in self.show.lines],
            'line': self.show.line.id,
            'date': self.show.line.date,
            'valuta_date': self.show.line.valuta_date,
            'contra_name': self.show.line.contra_name,
            'contra_account': self.show.line.contra_account,
            'contra_bank_code': self.show.line.contra_bank_code,
            'amount': self.show.line.amount,
            'purpose': self.show.line.purpose,
            'balance': self.show.line.balance,
            'kind': self.show.line.kind,
            'customer_ref': self.show.line.customer_ref,
            'code': self.show.line.code,
            'addkey': self.show.line.addkey,
            'primanota': self.show.line.primanota,
            'invoices': Transaction().context['invoices'],
            }
        return defaults

    def transition_save_lines(self):
        if self.show.batch_lines:
            for line in self.show.batch_lines:
                line.save()
                self.start.running_balance += line.amount
        return 'next_'

    def do_open_lines(self, action):
        journal_id = self.start.bank_import_config.journal.id

        self.start.bank_import_config._clean_warnings()
        # Use name from view_header_get
        del action['name']
        del action['rec_name']

        domain = [
            ('journal', '=', journal_id),
            ('move.state', '!=', 'posted'),
            ]
        ctx = {
            'journal': journal_id,
            }
        action['pyson_domain'] = PYSONEncoder().encode(domain)
        action['pyson_context'] = PYSONEncoder().encode(ctx)
        return action, {}

    def do_open_batch(self, action):
        pool = Pool()
        Batch = pool.get('account.batch')

        self.start.bank_import_config._clean_warnings()
        if not self.start.batch:
            return
        if not self.start.batch.lines:
            Batch.delete([self.start.batch])
            return

        batch_id = self.start.batch.id
        journal_id = self.start.journal.id
        domain = [
            ('journal', '=', journal_id),
            ('id', '=', batch_id),
            ]
        ctx = {
            'journal': journal_id,
            'batch': batch_id,
            }
        # Use name from view_header_get
        with Transaction().set_context(**ctx):
            header_name = Batch.view_header_get()
            action['name'] = header_name
            action['rec_name'] = header_name
        action['pyson_domain'] = PYSONEncoder().encode(domain)
        action['pyson_context'] = PYSONEncoder().encode(ctx)
        return action, {}
