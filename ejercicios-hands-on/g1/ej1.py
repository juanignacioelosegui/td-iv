'''
    No voy a hacer tres consultas de traceroute en tres momentos distintos del día.
    Tengo que dormir en algún momento.
'''

# para ejecutar comandos, saber el SO y trabajar con patrones en strings
import subprocess, platform, re
# para hacer la tabla por consola
from tabulate import tabulate

def parse_latency(latency_str):
    # Extrae número de ms (incluso si es '<1 ms' o '*')
    if "*" in latency_str:
        return -1
    match = re.search(r"(\d+)", latency_str)
    return int(match.group(1)) if match else -1

def traceroute(host):
    # averiguar SO del usuario
    system = platform.system()
    # el comando varia segun el SO
    if system == "Windows":
        command = ["tracert", host]
    else:
        ["traceroute", host]

    try:
        # ejecutar comando con texto plano y salidas estandar
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # parsear el resultado de consola
        output = result.stdout.splitlines()
    except Exception as e:
        return f"Error al ejecutar el comando: {e}"

    hops = []
    max_latency = -1
    max_latency_hop = None

    for line in output:
        if system == "Windows":
            # ???
            match = re.match(r"^\s*(\d+)\s+(<\d+ ms|\d+ ms|\*\s+\*\s+\*)\s+(.+?)(\s+\[(.*?)\])?", line)
            if match:
                # parsear caracteristicas de cada hop
                hop_num = match.group(1)
                latency = match.group(2)
                host = match.group(3).strip()
                ip = match.group(5) if match.group(5) else host
                latency_val = parse_latency(latency)
                
                # actualizar hop con mayor latencia
                if latency_val > max_latency:
                    max_latency = latency_val
                    max_latency_hop = hop_num
                
                hops.append([hop_num, f"{host} ({ip})", latency])
        else:
            match = re.match(r"^\s*(\d+)\s+([^\s]+)\s+\(([^)]+)\)\s+([\d.]+)\s+ms", line)
            if match:
                hop_num = match.group(1)
                host = match.group(2)
                ip = match.group(3)
                latency = match.group(4) + " ms"
                latency_val = float(match.group(4))

                if latency_val > max_latency:
                    max_latency = latency_val
                    max_latency_hop = hop_num
                
                hops.append([hop_num, f"{host} ({ip})", latency])

    # definir headers de tabla
    headers = ["Hop", "Host (IP)", "Latency"]
    # definir contenido de tabla
    table = tabulate(hops, headers=headers, tablefmt="grid")
    
    # imprimir hop con mayor delay
    if max_latency_hop:
        table += f"\n\n>> Mayor delay: hop #{max_latency_hop} con {max_latency} ms"
    return table

# programa principal
if __name__ == "__main__":
    destino = input("Ingrese el host o IP a trazar: ")
    print(traceroute(destino))


'''
    Me importa el último hop, que es el destino.
    Este va a ser lo que tarda un paquete IP en ir a destino y volver
'''