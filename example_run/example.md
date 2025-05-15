# Example Run of MySQL 8.0.42 on Ubuntu 24.04.2 LTS

I used `apt install mysql-server` to install MySQL, it installed MySQL 8.0.42.

I downloaded the thread_pool_hybrid repo and mysql-server git repo from github. Then I did switched the 8.0 repo and and set the HEAD at the tag 'mysql-8.0.42'

```
git clone https://github.com/Damienkatz/thread_pool_hybrid.git
git clone https://github.com/mysql/mysql-server.git
cd mysql-server
cp -r ../thread_pool_hybrid/ plugin/
git checkout mysql-8.0.42
cmake . -DBUILD_CONFIG=mysql_release -DFORCE_INSOURCE_BUILD=1
```

You will get configure errors here! Use `sudo apt install <packages>` to satisfy them. Sorry, I don't remember them all, but CMake will tell you each dependency that's missing. For example. boost. So google "apt install boost ubuntu" you'll find a page with how to install boost. Satisfy a dependecy, then run `cmake . -DBUILD_CONFIG=mysql_release -DFORCE_INSOURCE_BUILD=1` again. Satify the next dependency, lather repeat...

Once you've satified all the dependencies, don't build the whole of mysql from source! Unless you like waiting a long time. Instead...

```
cd plugin/thread_pool_hybrid
make
```

It should now build it and only the source code it relies on, and output the properly version lib to `mysql-server/plugin_output_directory/libthread_pool_hybrid.so` So then copy that to the mysql plugin directory.

```
 sudo cp ../../plugin_output_directory/libthread_pool_hybrid.so /usr/lib/mysql/plugin/
```

I turned off binlogging, increased the innodb buffer pool and increased max_connections and max_prepared_stmt_count in /etc/mysql/mysql.conf.d/mysqld.cnf. You can use this command:

```
echo "skip-log-bin
innodb_buffer_pool_size = 24G
innodb-buffer-pool-instances = 12
innodb-buffer-pool-chunk-size = 2G
max_connections = 500000
max_prepared_stmt_count = 10000000
" | sudo tee -a /etc/mysql/mysql.conf.d/mysqld.cnf
```

Now that you've changed the max connections to something massive, you have to set it in the OS and the mysql service file.

```
echo "fs.file-max = 500000" | sudo tee -a /etc/sysctl.conf
sudo gawk -i inplace '/LimitNOFILE/{gsub(/[0-9]+/, "500000")};{print}' /usr/lib/systemd/system/mysql.service
```

Now reboot the system.

```

I got the mysql admin account password from here:

'''
~$ sudo cat /etc/mysql/debian.cnf
# Automatically generated for Debian scripts. DO NOT TOUCH!
[client]
host     = localhost
user     = debian-sys-maint
password = foo
socket   = /tmp/mysqld.sock
[mysql_upgrade]
host     = localhost
user     = debian-sys-maint
password = foo
socket   = /tmp/mysqld.sock
'''





