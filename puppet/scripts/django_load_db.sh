!#/bin/bash

curl -O http://www.fuzzwork.co.uk/dump/mysql55-retribution-1.1-84566.tbz2
bunzip2 mysql55-retribution-1.1-84566.tbz2
tar xvf mysql55-retribution-1.1-84566.tar
mysql -u root -D djangotest < retribution-1.1-84566/mysql55-retribution-1.1-84566.sql
rm /home/vagrant/mysql55-inferno12-extended.sql
/vagrant/evewspace/manage.py syncdb --noinput
/vagrant/evewspace/manage.py migrate
/vagrant/evewspace/manage.py buildsystemdata
/vagrant/evewspace/manage.py loaddata /vagrant/evewspace/*/fixtures/*.json
/vagrant/evewspace/manage.py defaultsettings
/vagrant/evewspace/manage.py resetadmin
/vagrant/evewspace/manage.py syncrss
