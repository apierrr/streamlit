import docker
import time
import csv
import os
from datetime import datetime

DATA_FILE = "/app/data/stats.csv"
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Init CSV si nécessaire
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "container_name", "cpu_percent", "ram_usage_mb", "status"])

print("🚀 Logger démarré avec la méthode 'Double Check'...")

try:
    client = docker.from_env()
except:
    print("❌ Erreur Docker Socket")
    exit(1)

# La fonction de calcul (Identique à celle qui marchait)
def calculate_cpu(d_now, d_pre):
    try:
        cpu_delta = d_now["cpu_stats"]["cpu_usage"]["total_usage"] - d_pre["cpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = d_now["cpu_stats"]["system_cpu_usage"] - d_pre["cpu_stats"]["system_cpu_usage"]
        
        if "online_cpus" in d_now["cpu_stats"]:
            cpu_count = d_now["cpu_stats"]["online_cpus"]
        else:
            cpu_count = len(d_now["cpu_stats"]["cpu_usage"]["percpu_usage"])
        
        if system_delta > 0.0 and cpu_delta > 0.0:
            return round((cpu_delta / system_delta) * cpu_count * 100.0, 2)
    except:
        return 0.0
    return 0.0

while True:
    try:
        containers = client.containers.list(all=True)
        timestamp = datetime.now().strftime("%H:%M:%S")

        for c in containers:
            cpu = 0.0
            ram = 0.0
            
            if c.status == "running":
                try:
                    # --- LA MÉTHODE GAGNANTE ---
                    # 1. Première photo
                    stats_1 = c.stats(stream=False)
                    
                    # 2. On attend le petit délai crucial (0.5s)
                    time.sleep(0.5)
                    
                    # 3. Deuxième photo
                    stats_2 = c.stats(stream=False)
                    
                    # 4. Calcul immédiat
                    cpu = calculate_cpu(stats_2, stats_1)
                    
                    # Pour la RAM, on prend la dernière valeur
                    ram = stats_2["memory_stats"]["usage"] / (1024 * 1024)
                except Exception as e:
                    # print(f"Erreur calcul pour {c.name}: {e}")
                    pass
            
            # Écriture dans le fichier
            with open(DATA_FILE, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, c.name, cpu, round(ram, 1), c.status])
        
        print(f"✅ Données enregistrées à {timestamp}")
        
    except Exception as e:
        print(f"Erreur boucle principale: {e}")

    # On attend avant la prochaine salve de mesures
    time.sleep(5)