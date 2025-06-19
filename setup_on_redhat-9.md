# Example Run of MySQL 9.3.0 on Red Hat Enterprise Linux 9

NOTE: this probably has mistakes. If you get stuck email me@damienkatz.com for what you are stuck on and I'll help get you unstuck.

I downloaded the mysql-enterprise-9.3.0_el9_x86_64_bundle.tar from oracle and uploaded to the test server in the ec2-user home dir.

I git cloned the this repo, thread_pool_hybrid repo and mysql-server repo from github. Then I set the HEAD of mysql-server at the tag 'mysql-8.0.42' and copied the thread_pool_hybrid files into the mysql repo, then did a cmake configure.

```
cd ~
tar xvf mysql-enterprise-9.3.0_el9_x86_64_bundle.tar
sudo yum install mysql-commercial-{server,client,client-plugins,icu-data-files,common,libs}-*
sudo service mysqld start
git clone https://github.com/Damienkatz/thrustdb_benchmarks.git
git clone https://github.com/Damienkatz/thread_pool_hybrid.git
git clone https://github.com/mysql/mysql-server.git
cd mysql-server
sudo yum install git cmake libaio-devel gcc-toolset-13-gcc gcc-toolset-13-gcc-c++ gcc-toolset-13-binutils gcc-toolset-13-annobin-annocheck gcc-toolset-13-annobin-plugin-gcc openssl-devel rpcgen flex bison

git checkout mysql-9.3.0
cp -r ../thread_pool_hybrid/ plugin/
echo "" > rpc.h
sudo mv rpc.h /usr/include/rpc/
cmake . -DBUILD_CONFIG=mysql_release -DFORCE_INSOURCE_BUILD=1
```

Don't build the whole of mysql from source! Instead...

```
cd plugin/thread_pool_hybrid
make
```

It should now build it and only the source code it relies on, and output the properly version lib to `mysql-server/plugin_output_directory/thread_pool_hybrid.so` So then copy that to the mysql plugin directory.

```
 sudo cp ../../plugin_output_directory/thread_pool_hybrid.so /usr/lib64/mysql/plugin/
```

Now increase the open file limit to something big!

```
echo "fs.file-max = 500000" | sudo tee -a /etc/sysctl.conf
sudo gawk -i inplace '/LimitNOFILE/{gsub(/[0-9]+/, "500000")};{print}' /usr/lib/systemd/system/mysqld.service
sudo sysctl -p
sudo systemctl daemon-reload
```

Now reboot your system.

#Install and configure the benchmark tool

```
cd ~/thrustdb_benchmarks
sudo tar -xvzf BMK-kit.tgz -C /
sudo cp set_env.sh perf_test_redhat.sh my.cnf-redhat9-enterprise_thread_pool my.cnf-redhat9-thread_pool_hybrid /BMK
sudo chown -R ec2-user:ec2-user /BMK
```

grep the file that has the mysql admin user and password.

```
~$  sudo grep password /var/log/mysqld.log
2025-06-18T19:50:54.968030Z 6 [Note] [MY-010454] [Server] A temporary password is generated for root@localhost: [password]
```

Then use the mysql client to change the password, also create the sysbench test database.

```
mysql -u root -p

mysql> ALTER USER 'username'@'host' IDENTIFIED BY '[new password]';
mysql> CREATE DATABASE sysbench;
mysql> quit
```

Now edit the .bench file in /BMK/ and fill in the fields.

```
cd /BMK
vim .bench
```

```
...
  user=root
  pass=[password]
  host=localhost
  port=3606
  socket=/var/lib/mysql/mysql.sock
  mysql=/usr/bin/mysql
...
```


Now edit the set_env.sh file in /BMK/ and fill in the fields.

```
vim set_env.sh
```

```
#!/bin/bash

export mysqladmin=root
export mysqladminpassword=[password]
export mysqlsocket=/var/lib/mysql/mysql.sock
export resultsdir=/home/ec2-user/results
```

I was getting errors attempting to run the `time bash /BMK/sb_exec/sb11-Prepare_10M_8tab-InnoDB.sh 32` command. So I did this:

```
sudo link /var/lib/mysql/mysql.sock /tmp/mysql.sock
```

Now you can run the benchmark tool. First I ran the prepare script, then my perf_test_redhat.sh tool.

```
time bash /BMK/sb_exec/sb11-Prepare_10M_8tab-InnoDB.sh 32
./perf_test_redhat.sh sb11-OLTP_RO_10M_8tab-pareto-trx-socket.sh sb11-OLTP_RO_10M_8tab-pareto-sum_ranges1-notrx-socket.sh sb11-OLTP_RO_10M_8tab-pareto-p_sel1-notrx-socket.sh sb11-OLTP_RO_1M_8tab-pareto-ps-p_sel1-reconnect-notrx-socket.sh sb11-OLTP_RO_10M_8tab-pareto-s_ranges1-notrx-socket.sh sb11-OLTP_RO_10M_8tab-uniform-p_sel1-reconnect-notrx-socket.sh
```

Now install the graph-cli through python pip to generate the graphs.

```
python3 -m venv ~/python
export PATH=/home/ec2-user/python/bin:$PATH
pip3 install graph-cli

python ~/thrustdb_benchmarks/generate_graphs.py ~/results/
```

In the ~/results/ directory will be your graph *.png files.

See thread_pool_hybrid_vs_enterprise_thread_pool-mysql-9.0.3-redhat_9.0.4-r7i.4xlarge.md for an example graph output of all of the above.

