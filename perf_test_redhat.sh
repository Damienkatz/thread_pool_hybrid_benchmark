#!/bin/bash

source ./set_env.sh

testlength=90;
for script in "$@"; do
        handler="-thread_pool_hybrid";
        while ! sudo service mysql status | grep -q "Active: active (running)" ; do sleep 1; done
        sudo cp my.cnf-redhat9-thread_pool_hybrid /etc/my.cnf
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
                        rm -f $resultsdir/tmp_perf_values.txt;
                        rm -f $resultsdir/tmp_process_stats.txt;
                        break;
                elif [[ "$mysqldpid" != "$mysqldpid2" ]] ; then
                        echo "mysql crashed during execution. terminating test at $users users";
                        rm -f $resultsdir/tmp_perf_values.txt;
                        rm -f $resultsdir/tmp_process_stats.txt;
                        break;
                elif grep -Fq "FATAL: " $resultsdir/tmp_perf_values.txt ; then
                        echo "test failure. terminating test at $users users";
                        rm -f $resultsdir/tmp_perf_values.txt;
                        rm -f $resultsdir/tmp_process_stats.txt;
                        break;
                else
                        echo "Clients: $users" >> $resultsdir/$script$handler.txt
                        cat $resultsdir/tmp_perf_values.txt >> $resultsdir/$script$handler.txt;
                        cat $resultsdir/tmp_process_stats.txt >> $resultsdir/$script$handler.txt;
                        echo "end process stats" >> $resultsdir/$script$handler.txt;
                fi;
                rm -f $resultsdir/tmp_perf_values.txt;
                rm -f $resultsdir/tmp_process_stats.txt;
        done;
        sleep 30

        handler="-enterprise_thread_pool";
        while ! sudo service mysql status | grep -q "Active: active (running)" ; do sleep 1; done
        sudo cp my.cnf-redhat9-enterprise_thread_pool /etc/my.cnf
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
                        rm -f $resultsdir/tmp_perf_values.txt;
                        rm -f $resultsdir/tmp_process_stats.txt;
                        break;
                elif [[ "$mysqldpid" != "$mysqldpid2" ]] ; then
                        echo "mysql crashed during execution. terminating test at $users users";
                        rm -f $resultsdir/tmp_perf_values.txt;
                        rm -f $resultsdir/tmp_process_stats.txt;
                        break;
                elif grep -Fq "FATAL: " $resultsdir/tmp_perf_values.txt ; then
                        echo "test failure. terminating test at $users users";
                        rm -f $resultsdir/tmp_perf_values.txt;
                        rm -f $resultsdir/tmp_process_stats.txt;
                        break;
                else
                        echo "Clients: $users" >> $resultsdir/$script$handler.txt
                        cat $resultsdir/tmp_perf_values.txt >> $resultsdir/$script$handler.txt;
                        cat $resultsdir/tmp_process_stats.txt >> $resultsdir/$script$handler.txt;
                        echo "end process stats" >> $resultsdir/$script$handler.txt;
                fi;
                rm -f $resultsdir/tmp_perf_values.txt;
                rm -f $resultsdir/tmp_process_stats.txt;
        done;
        sleep 30
done;
