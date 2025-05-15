import os
import sys
import re

class Stats:
    def __init__(self):
        self.clients = 0
        self.events_sec = 0.0
        self.avg_latency_ms = 0.0
        self.per95th_latency_ms = 0.0
        self.avg_user_cpu = 0.0
        self.avg_system_cpu = 0.0
        self.max_virtual_mb = 0.0
        self.max_resident_mb = 0.0


def extract_next_stats(file):
    clients = 0
    perfvalues_list = []
    procvalues_list = []

    class PerfValues:
        def __init__(self):
            self.clients = 0
            self.time_secs = 0.0
            self.events = 0
            self.avg_latency_ms = 0.0
            self.per95th_latency_ms = 0.0
    
    class ProcValues:
        def __init(self):
            self.user_cpu
            self.system_cpu
            self.virtual_mb
            self.resident_mb

    while True:
        line = file.readline()

        if len(line) == 0:
            break
        if line.startswith("Clients:"):
            clients = int(line.split(" ")[-1].strip())
            break
    
    if clients == 0:
        return Stats()
    
    perfvals = PerfValues()

    while clients != 0:
        line = file.readline()
        
        if line.startswith("Number of threads: "):
            perfvals.clients = int(line.split(" ")[-1].strip())
            clients = clients - perfvals.clients

            while True:
                line = file.readline()

                if len(line) == 0:
                    break
                if line.startswith("    time elapsed:"):
                    perfvals.time_secs = float(re.sub('s', '',line).split(" ")[-1].strip())
                    break

            while True:
                line = file.readline()

                if len(line) == 0:
                    break
                if line.startswith("    total number of events:"):
                    perfvals.events = int(line.split(" ")[-1].strip())
                    break

            while True:
                line = file.readline()

                if len(line) == 0:
                    break
                if line.startswith("         avg:"):
                    perfvals.avg_latency_ms = float(line.split(" ")[-1].strip())
                    break

            while True:
                line = file.readline()

                if len(line) == 0:
                    break
                if line.startswith("         95th percentile:"):
                    perfvals.per95th_latency_ms = float(line.split(" ")[-1].strip())
                    break

            perfvalues_list.append(perfvals)
            perfvals = PerfValues()

    procvals = ProcValues()

    while True:
        line = file.readline()

        if len(line) == 0:
            break
        if line.startswith("end process stats"):
            break
        if line.startswith("# Time "):
            line = file.readline()
            line = re.sub(' +', ' ', line).split(" ")
            procvals.user_cpu = float(line[3])
            procvals.system_cpu = float(line[4])
            procvals.virtual_mb = float(line[11])/1000
            procvals.resident_mb = float(line[12])/1000
            procvalues_list.append(procvals)
            procvals = ProcValues()

    stats = Stats()
    
    time_secs_weighted = 0.0
    events = 0
    avg_latency_ms_weighted = 0.0
    per95th_latency_ms_weighted = 0.0
    
    for perfvals in perfvalues_list:
        stats.clients = stats.clients + perfvals.clients
        time_secs_weighted = time_secs_weighted + float(perfvals.clients) * perfvals.time_secs
        events = events + perfvals.events
        avg_latency_ms_weighted = avg_latency_ms_weighted + float(perfvals.clients) * perfvals.avg_latency_ms
        per95th_latency_ms_weighted = per95th_latency_ms_weighted + float(perfvals.clients) * perfvals.per95th_latency_ms

    time_secs = time_secs_weighted/stats.clients
    stats.events_sec = float(events)/time_secs
    stats.avg_latency_ms = avg_latency_ms_weighted/stats.clients
    stats.per95th_latency_ms = per95th_latency_ms_weighted/stats.clients

    sum_user_cpu = 0.0
    sum_system_cpu = 0.0
    
    for procvals in procvalues_list:
        sum_user_cpu = sum_user_cpu + procvals.user_cpu
        sum_system_cpu = sum_system_cpu + procvals.system_cpu
        stats.max_virtual_mb = max(stats.max_virtual_mb, procvals.virtual_mb)
        stats.max_resident_mb = max(stats.max_resident_mb, procvals.resident_mb)
    
    stats.avg_user_cpu = sum_user_cpu/len(procvalues_list)
    stats.avg_system_cpu = sum_system_cpu/len(procvalues_list)
    return stats

if len(sys.argv) > 1:
    dir = sys.argv[1]
    listdir = sys.argv[1]
else:
    dir = ""
    listdir = "."
testList = [i for i in os.listdir(listdir) if i.startswith("sb11-") and i.endswith(".txt")]
testList = [i.replace("-thread_pool_hybrid.txt", "") for i in testList if i.endswith("-thread_pool_hybrid.txt") and \
            i.replace("-thread_pool_hybrid.txt", "-connection_per_thread.txt") in testList]
print(testList)

for test in testList:
    print("Attempting " + test)
    file_tph = open(dir + test + '-thread_pool_hybrid.txt', 'r')
    file_cpt = open(dir + test + '-connection_per_thread.txt', 'r')
    
    events_sec_csv = open(dir + test + "-events_sec.csv", "w")
    events_sec_csv.write("x,thread pool hybrid,connection per thread\n")

    latency_csv = open(dir + test + "-latency.csv", "w")
    latency_csv.write("x,thread pool hybrid - latency 95th % ms,thread pool hybrid - latency average ms," +
                    "connection per thread - latency 95th % ms,connection per thread - latency average ms\n")
    
    cpu_csv = open(dir + test + "-cpu.csv", "w")
    cpu_csv.write("x,thread pool hybrid - avg user cpu,thread pool hybrid - avg system cpu," +
                    "connection per thread - avg user cpu,connection per thread - avg system cpu\n")
    
    memory_csv = open(dir + test + "-memory.csv", "w")
    memory_csv.write("x,thread pool hybrid - max virtual memory mb,thread pool hybrid - max resident memory mb," +
                    "connection per thread - max virtual memory mb,connection per thread - max resident memory mb\n")

    while True:
        stats_tph = extract_next_stats(file_tph)
        stats_cpt = extract_next_stats(file_cpt)

        if stats_tph.clients == 0 and stats_cpt.clients == 0:
            events_sec_csv.close()
            latency_csv.close()
            cpu_csv.close()
            memory_csv.close()
            break
        elif stats_tph.clients == 0:
            clients = stats_cpt.clients
        else:
            clients = stats_tph.clients

        line = str(clients) + "," + str(stats_tph.events_sec) + "," + str(stats_cpt.events_sec) + "\n"
        events_sec_csv.write(line)

        line = str(clients) + "," + str(stats_tph.per95th_latency_ms) + "," + str(stats_tph.avg_latency_ms) \
                + "," + str(stats_cpt.per95th_latency_ms) + "," + str(stats_cpt.avg_latency_ms) + "\n"
        latency_csv.write(line)

        line = str(clients) + "," + str(stats_tph.avg_user_cpu) + "," + str(stats_tph.avg_system_cpu) \
                + "," + str(stats_cpt.avg_user_cpu) + "," + str(stats_cpt.avg_system_cpu) + "\n"
        cpu_csv.write(line)

        line = str(clients) + "," + str(stats_tph.max_virtual_mb) + "," + str(stats_tph.max_resident_mb) \
                + "," + str(stats_cpt.max_virtual_mb) + "," + str(stats_cpt.max_resident_mb) + "\n"
        memory_csv.write(line)
        
    os.system("graph " + dir + test + "-events_sec.csv" + " --bar --title \"THROUGHPUT - " + \
              test + "\" --xlabel clients --ylabel events/sec --fontsize 10 --output " + dir + test + "-1_events_sec.png")
    
    os.system("graph " + dir + test + "-latency.csv" + " --bar --title \"LATENCY - " + \
              test + "\" --xlabel clients --ylabel \"latency ms\" --color steelblue,lightsteelblue,#EF8636,sandybrown --fontsize 10 --output " + dir + test + "-2_latency.png")

    os.system("graph " + dir + test + "-cpu.csv" + " --bar --title \"CPU - " + \
              test + "\" --xlabel clients --ylabel \"cpu %\" --color steelblue,lightsteelblue,#EF8636,sandybrown --fontsize 10 --output " + dir + test + "-4_cpu.png")

    os.system("graph " + dir + test + "-memory.csv" + " --bar --title \"MEMORY - " + \
              test + "\" --xlabel clients --ylabel \"memory mb\" --color steelblue,lightsteelblue,#EF8636,sandybrown --fontsize 10 --output " + dir + test + "-3_memory.png")
