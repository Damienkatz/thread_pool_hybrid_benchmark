# Example Run of MySQL 8.0.42 on Ubuntu 24.04.2 LTS

NOTE: this probably has mistakes and likely only works on Ubuntu 24.04. If you get stuck email me@damienkatz.com for what you are stuck on and I'll help get you unstuck.

I used `apt install mysql-server` to install MySQL, it installed MySQL 8.0.42.

I git cloned the this repo, thread_pool_hybrid repo and mysql-server repo from github. Then I set the HEAD of mysql-server at the tag 'mysql-8.0.42' and copied the thread_pool_hybrid files into the mysql repo, then did a cmake configure.

```
cd ~
git clone https://github.com/Damienkatz/thrustdb_benchmarks.git
git clone https://github.com/Damienkatz/thread_pool_hybrid.git
git clone https://github.com/mysql/mysql-server.git
cd mysql-server
git checkout mysql-8.0.42
cp -r ../thread_pool_hybrid/ plugin/
cmake . -DBUILD_CONFIG=mysql_release -DFORCE_INSOURCE_BUILD=1
```

You will get configure errors here! Use `sudo apt install <packages>` to satisfy them. Sorry, I don't remember them all, but CMake will tell you each dependency that's missing. For example, boost. So google "apt install boost ubuntu" you'll find a page with how to install boost. Satisfy a dependecy, then run `cmake . -DBUILD_CONFIG=mysql_release -DFORCE_INSOURCE_BUILD=1` again. Satify the next dependency, lather repeat...

Once you've satified all the dependencies, don't build the whole of mysql from source! Unless you like waiting a long time. Instead...

```
cd plugin/thread_pool_hybrid
make
```

It should now build it and only the source code it relies on, and output the properly version lib to `mysql-server/plugin_output_directory/libthread_pool_hybrid.so` So then copy that to the mysql plugin directory.

```
 sudo cp ../../plugin_output_directory/libthread_pool_hybrid.so /usr/lib/mysql/plugin/
```

In MySQL, I turned off binlogging, increased the innodb buffer pool and increased max_connections and max_prepared_stmt_count in /etc/mysql/mysql.conf.d/mysqld.cnf. You can use this command:

```
echo "skip-log-bin
innodb_buffer_pool_size = 24G
innodb-buffer-pool-instances = 12
innodb-buffer-pool-chunk-size = 2G
max_connections = 100000
max_prepared_stmt_count = 10000000
" | sudo tee -a /etc/mysql/mysql.conf.d/mysqld.cnf
```

Now that you've changed the max connections to the maximum 100000, you have to set it in the OS and the mysql service file.

```
echo "fs.file-max = 500000" | sudo tee -a /etc/sysctl.conf
sudo gawk -i inplace '/LimitNOFILE/{gsub(/[0-9]+/, "500000")};{print}' /usr/lib/systemd/system/mysql.service
sudo sysctl -p
```

#Install and configure the benchmark tool

```
cd ~/thrustdb_benchmarks
sudo tar -xvzf BMK-kit.tgz -C /
sudo cp set_env.sh perf_test_ubuntu.sh /BMK
sudo chown -R ubuntu:ubuntu /BMK
```

cat the file that has the mysql admin user and password.

```
~$ sudo cat /etc/mysql/debian.cnf
# Automatically generated for Debian scripts. DO NOT TOUCH!
[client]
host     = localhost
user     = debian-sys-maint
password = [password]
socket   = /var/run/mysqld/mysqld.sock
[mysql_upgrade]
host     = localhost
user     = debian-sys-maint
password = [password]
socket   = /var/run/mysqld/mysqld.sock
```

Now edit the .bench file in /BMK/ and fill in the fields.

```
cd /BMK
vim .bench
```

```
...
  user=debian-sys-maint
  pass=[password]
  host=localhost
  port=3606
  socket=/var/run/mysqld/mysqld.sock
  mysql=/usr/bin/mysql
...
```


Now edit the set_env.sh file in /BMK/ and fill in the fields.

```
vim set_env.sh
```

```
#!/bin/bash

export mysqladmin=debian-sys-maint
export mysqladminpassword=[password]
export mysqlsocket=/var/run/mysqld/mysqld.sock
export resultsdir=/home/ubuntu/results
```

Now you can run the benchmark tool. First I ran the prepare script, then my perf_test.sh tool.

```
time bash /BMK/sb_exec/sb11-Prepare_10M_8tab-InnoDB.sh 32
./perf_test_ubuntu.sh sb11-OLTP_RO_10M_8tab-pareto-trx-socket.sh sb11-OLTP_RO_10M_8tab-pareto-sum_ranges1-notrx-socket.sh sb11-OLTP_RO_10M_8tab-pareto-p_sel1-notrx-socket.sh sb11-OLTP_RO_1M_8tab-pareto-ps-p_sel1-reconnect-notrx-socket.sh sb11-OLTP_RO_10M_8tab-pareto-s_ranges1-notrx-socket.sh sb11-OLTP_RO_10M_8tab-uniform-p_sel1-reconnect-notrx-socket.sh
```

Now install the graph-cli through python pip to generate the graphs.

```
sudo apt install python3.12-venv
python3 -m venv ~/python
export PATH=/home/ubuntu/python/bin:$PATH
pip3 install graph-cli

python ~/thrustdb_benchmarks/generate_graphs.py ~/results/
```

In the ~/results/ directory will be your graph *.png files.

See thread_pool_hybrid-vs-connection_per_thread-mysql_8.0.4-ubuntu_24.04-on-r5.8xlarge.md for an example graph output of all of the above.

