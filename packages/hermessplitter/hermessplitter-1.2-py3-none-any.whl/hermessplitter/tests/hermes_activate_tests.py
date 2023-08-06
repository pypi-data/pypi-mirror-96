from hermessplitter.main import HermesSplitter

hs = HermesSplitter('0.0.0.0', 2295, 'hermes', 'watchman', 'hect0r1337', '192.168.100.109',
                    'wdb', 'watchman', 'hect0r1337', '192.168.100.109', debug=True)
hs.activate(carnum='В060ХА702')
all_data = ['100', '500', '1000']
for data in all_data:
    hs.make_magic(data)