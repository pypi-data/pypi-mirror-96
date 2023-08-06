import random


def check_hermes_active(sqlshell):
    # Проверка статус Hermes на активность
    command = "SELECT active FROM kf_table"
    hermes_info = sqlshell.try_execute_get(command)
    hermes_activity = hermes_info[0][0]
    print('\nПолучена активность Hermes', hermes_activity)
    if hermes_activity:
        return True

def get_hermes_general_kf(hermes_sqlshell):
    # Проверка статус Hermes на активность
    command = "SELECT kf FROM kf_table where name='Общий'"
    hermes_info = hermes_sqlshell.try_execute_get(command)
    general_kf = hermes_info[0][0] * 0.01
    print('\nПолучена активность Hermes', general_kf)
    return general_kf

def get_max_weight(sqlshell, carnum):
    command = "SELECT max(brutto) FROM records WHERE car_number='{}'".format(carnum)
    weight = get_weight(sqlshell, command)
    return weight


def set_kf_randomize(self):
    self.kf_randomize = self.get_kf_randomize(0.9, 1.1)


def set_kf_randomized(self):
    self.kf_randomized = self.get_kf_randomized(self.kf, self.kf_randomize)

def get_weight(sqlshell, command):
    weight_tuple = sqlshell.try_execute_get(command)
    weight = weight_tuple[0][0]
    return weight


def get_avg_tara(sqlshell, carnum):
    # print('\tDK 7. Getting avg weight')
    command = "SELECT avg(tara) FROM records WHERE car_number='{}'".format(carnum)
    weight = get_weight(sqlshell, command)
    return weight


def get_avg_weight(sqlshell, carnum):
    # print('\tDK 7. Getting avg weight')
    command = "SELECT avg(cargo) FROM records WHERE car_number='{}'".format(carnum)
    weight = get_weight(sqlshell, command)
    return weight


def get_kf(wdb_sqlshell, hermes_sqlshell, carrier=None, kf=None):
    print(locals())
    if not kf and carrier:
        kf = get_hermes_kf(wdb_sqlshell, carrier)
    elif not kf and not carrier:
        kf = get_hermes_general_kf(hermes_sqlshell)
    else:
        kf = 0
    # Получаем рандомное значение* в диапазоне (рандомайзер)
    kf_randomize = get_kf_randomize(0.9, 1.1)
    # Умножаем kf на рандомайзер
    kf = get_kf_randomized(kf, kf_randomize)
    return kf


def get_kf_randomize(min, max):
    # Вернуть рандомайзер
    added = random.uniform(min, max)
    return added


def get_kf_randomized(kf, kf_randomize):
    # Рандомизировать kf умножив его на рандомайзер
    kf = kf * kf_randomize
    return kf


def get_hermes_kf_info(sqlshell, carrier):
    command = "SELECT kf FROM clients where id_1c='{}'".format(carrier)
    hermes_kf_info = sqlshell.try_execute_get(command)
    return hermes_kf_info


def get_hermes_kf(sqlshell, carrier):
    # Лезет в БД Hermes и получает нужный коэффициент
    hermes_kf = get_hermes_kf_info(sqlshell, carrier)
    hermes_kf = hermes_kf[0][0]
    hermes_kf = int(hermes_kf) * 0.01
    print('Получен KF Hermes =', hermes_kf)
    return hermes_kf
