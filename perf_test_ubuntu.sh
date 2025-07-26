#!/bin/bash

source ./set_env.sh

testlength=90;
for script in "$@"; do
        for handler in "-thread_pool_hybrid" "-connection_per_thread"; do
                while ! sudo service mysql status | grep -q "Active: active (running)" ; do sleep 1; done
                if [[ "$$handler" != "-connection_per_thread" ]] ; then
                        mysql -u $mysqladmin -p$mysqladminpassword -S $mysqlsocket -e \
                                "INSTALL PLUGIN THREAD_POOL_HYBRID SONAME 'thread_pool_hybrid.so';" ;
                elif [[ "$$handler" != "-thread_pool_hybrid" ]] ; then
                        mysql -u $mysqladmin -p$mysqladminpassword -S $mysqlsocket -e \
                                "UNINSTALL PLUGIN THREAD_POOL_HYBRID;" 2> /dev/null;
                fi;
                sudo service mysql restart;
                echo "Warming up filesystem cache";
                /BMK/sb_exec/$script 1024 $testlength >> /dev/null;
                mysqldpid=`pidof mysqld`;
                echo "Writing to $script$handler.txt";
                echo "" > $resultsdir/$script$handler.txt;
                for users in 1 4 16 64 256 1024 4096 16384 32768 65536 98304; do
                        echo "Attempting $users clients";
                        pidstat -u -r -h -p `pidof mysqld` 5 100 > $resultsdir/tmp_process_stats.txt&
                        /BMK/sb_exec/$script $users $testlength > $resultsdir/tmp_perf_values.txt;
                        exit_code=$?;
                        killall pidstat;
                        mysqldpid2=`pidof mysqld`;
                        if [[ $exit_code -ne 0 ]] ; then
                                echo "sysbench failed during execution. terminating test at $users users";
                        elif [[ "$mysqldpid" != "$mysqldpid2" ]] ; then
                                echo "mysql crashed during execution. terminating test at $users users";
                        elif grep -Fq "FATAL: " $resultsdir/tmp_perf_values.txt ; then
                                echo "test failure. terminating test at $users users";
                        else
                                echo "Clients: $users" >> $resultsdir/$script$handler.txt
                                cat $resultsdir/tmp_perf_values.txt >> $resultsdir/$script$handler.txt;
                                cat $resultsdir/tmp_process_stats.txt >> $resultsdir/$script$handler.txt;
                                echo "end process stats" >> $resultsdir/$script$handler.txt;
                        fi;
                        rm $resultsdir/tmp_perf_values.txt;
                        rm $resultsdir/tmp_process_stats.txt;
                done;
                sleep 30
        done;
done;
