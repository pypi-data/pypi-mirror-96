from weightsplitter.main import WeightSplitter
from traceback import format_exc
from wsqluse.wsqluse import Wsqluse
from hermessplitter import functions


class HermesSplitter(WeightSplitter):
    def __init__(self, ip, port, hermes_db_name, hermes_db_user, hermes_db_pass, hermes_db_host,
                 wdb_name, wdb_user, wdb_pass, wdb_host,
                 port_name='/dev/ttyUSB0', terminal_name='CAS',
                 debug=False):
        super().__init__(ip, port, debug=debug, port_name=port_name, terminal_name=terminal_name)
        self.active = False
        self.kf = 0
        self.hermes_weight = 0
        self.avg_tara = 0
        self.max_brutto = 0
        self.avg_weight = 0
        self.hermes_sqlshell = Wsqluse(hermes_db_name, hermes_db_user, hermes_db_pass, hermes_db_host)
        self.wdb_sqlshell = Wsqluse(wdb_name, wdb_user, wdb_pass, wdb_host)


    def activate(self, carnum, kf=0.19):
        """ Активировать HERMES """
        if functions.check_hermes_active(self.hermes_sqlshell):
            kf = functions.get_kf(self.wdb_sqlshell, kf=kf)
            avg_tara = functions.get_avg_tara(self.wdb_sqlshell, carnum)
            max_brutto = functions.get_max_weight(self.wdb_sqlshell, carnum)
            avg_weigth = functions.get_avg_weight(self.wdb_sqlshell, carnum)
            self.set_kf(kf)
            self.set_status(True)
            self.set_debug(self.debug)
            self.set_avg_tara(avg_tara)
            self.set_max_brutto(max_brutto)
            self.set_avg_weigth(avg_weigth)

    def set_kf(self, kf):
        self.show_print('setting kf', kf, debug=True)
        self.kf = 1.0 + kf

    def set_debug(self, debug):
        self.debug = debug

    def set_status(self, status):
        self.show_print('settings status', status, debug=True)
        self.active = status
        if not status:
            self.hermes_weight = 0

    def set_avg_tara(self, avg_tara):
        try:
            self.avg_tara = int(avg_tara)
        except:
            self.show_print(self.avg_tara, '-  ЭТО НЕ ЧИСЛО')
            self.avg_tara = 0

    def set_max_brutto(self, max_brutto):
        try:
            self.max_brutto = int(max_brutto)
        except:
            self.show_print(self.max_brutto, '-  ЭТО НЕ ЧИСЛО')
            self.max_brutto = 0
        self.netto_max = self.max_brutto - self.avg_tara

    def send_data(self, data):
        data = self.make_magic(data)
        super().send_data(data)

    def set_avg_weigth(self, weight):
        try:
            self.avg_weight = int(weight)
        except:
            self.show_print(self.avg_weight, '-  ЭТО НЕ ЧИСЛО')
            self.avg_weight = 0

    def make_magic(self, data):
        try:
            if self.active and data.isdigit() and self.avg_tara != 0 and self.max_brutto != 0 and self.avg_weight != 0:
                self.show_print('It`s active! KF', self.kf, debug=True)
                self.show_print('Increasing. data', data, debug=True)
                self.show_print('avg_tara', self.avg_tara, debug=True)
                self.show_print('avg_weight', self.avg_weight, debug=True)

                # 3 положение
                approx_netto = float(data) - float(self.avg_tara)
                self.show_print('approximate netto is', approx_netto)
                delta_k = approx_netto * float(self.kf) - approx_netto
                self.show_print('new delta_k', delta_k, debug=True)

                # 1 Положение
                avg_delta = self.avg_weight * self.kf - self.avg_weight
                if float(delta_k) > float(avg_delta):
                    delta_k = float(avg_delta)
                self.show_print('avg_delta', avg_delta, debug=True)

                # 5 положение
                if int(delta_k) > 0:
                    new_data = float(data) + float(delta_k)
                else:
                    new_data = data

                # 2 положение
                if float(new_data) > float(self.max_brutto):                     # 2 Положение
                    new_data = data
                new_data = str(self.make_data_aliquot(new_data))
                self.show_print('New data', new_data)
                self.show_print('Old data', data)
                self.hermes_weight = int(new_data) - int(data)
                if self.debug:
                    new_data = data
            else:
                new_data = data
        except:
            new_data = data
            self.show_print(format_exc())
        return str(new_data)

    def make_netto_less(self, added, br_diff, kf):
        delta_k = added * kf
        if delta_k > br_diff: #решить с кэфом
            over = delta_k - br_diff
            delta_k = delta_k - over * 1.1
        return delta_k

