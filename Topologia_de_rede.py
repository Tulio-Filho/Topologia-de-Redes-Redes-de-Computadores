import ipaddress
import random
import networkx as nx
import matplotlib.pyplot as plt
import time

# Função para simular o ping
def simular_ping():
    return random.randint(10, 200)  # Simulando latência entre 10ms e 200ms

# Função para gerar os endereços IP de uma sub-rede
def alocar_enderecos(rede, num_hosts):
    return list(rede.hosts())[:num_hosts]


# Definição das sub-redes para switches de borda
sub_redes12 = [
    ipaddress.IPv4Network('192.168.2.0/27'),
    ipaddress.IPv4Network('192.168.2.32/27'),
    ipaddress.IPv4Network('192.168.2.64/27'),
    ipaddress.IPv4Network('192.168.2.96/27')

]

sub_redes = [
    ipaddress.IPv4Network('192.168.3.0/27'),
    ipaddress.IPv4Network('192.168.3.32/27'),
    ipaddress.IPv4Network('192.168.3.64/27'),
    ipaddress.IPv4Network('192.168.3.96/27')
]

hosts_por_rede3_4 = 15 
hosts_por_rede1_2 = 24  # Quantidade de hosts por switch de borda
hosts = {f'hosts_e{i+1}': alocar_enderecos(sub_redes12[i], hosts_por_rede1_2) for i in range(len(sub_redes))} | {f'hosts_e{i+5}': alocar_enderecos(sub_redes[i], hosts_por_rede3_4) for i in range(len(sub_redes))}
# Definição dos switches
# Definição dos switches
switch_central = {"Switch_Central": "192.168.1.1"}

# Atualizando IPs e criando 4 switches de borda para cada switch de agregação
switches_agregacao = {
    "Switch_A1": "192.168.2.0",
    "Switch_A2": "192.168.3.0"
}

switches_borda = {
    "Switch_B1": "192.168.2.10",
    "Switch_B2": "192.168.2.20",
    "Switch_B3": "192.168.2.30",
    "Switch_B4": "192.168.2.40",
    "Switch_B5": "192.168.3.10",
    "Switch_B6": "192.168.3.20",
    "Switch_B7": "192.168.3.30",
    "Switch_B8": "192.168.3.40"
}

# Definição dos enlaces
enlaces = {
    ("Switch_Central", "Switch_A1"): {"tipo": "fibra óptica", "capacidade": "10 Gbps"},
    ("Switch_Central", "Switch_A2"): {"tipo": "fibra óptica", "capacidade": "10 Gbps"},
    ("Switch_A1", "Switch_B1"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A1", "Switch_B2"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A1", "Switch_B3"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A1", "Switch_B4"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A2", "Switch_B5"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A2", "Switch_B6"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A2", "Switch_B7"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"},
    ("Switch_A2", "Switch_B8"): {"tipo": "fibra óptica", "capacidade": "1 Gbps"}
}

# Tabelas de roteamento estáticas
tabelas_roteamento = {
    "Switch_Central": {
        "192.168.1.0/27": "Switch_A1",
        "192.168.1.32/27": "Switch_A1",
        "192.168.1.64/27": "Switch_A2",
        "192.168.1.96/27": "Switch_A2"
    },
    "Switch_A1": {
        "192.168.2.0/27": "Switch_B1",
        "192.168.2.32/27": "Switch_B2",
        "192.168.2.64/27": "Switch_B3",
        "192.168.2.96/27": "Switch_B4"
    },
    "Switch_A2": {
        "192.168.3.0/27": "Switch_B5",
        "192.168.3.32/27": "Switch_B6",
        "192.168.3.64/27": "Switch_B7",
        "192.168.3.96/27": "Switch_B8"
    }
}

def mostrar_tabelas_roteamento(G):
    print("\nTabelas de Roteamento:")
    for roteador, tabela in tabelas_roteamento.items():
        print(f"\n{roteador}:")
        for rede, proximo_salto in tabela.items():
            print(f"  {rede} -> {proximo_salto}")
    
    print("\nEndereços IP de todos os hosts no grafo:")
    for node, data in G.nodes(data=True):
        if data.get('type') == 'host':  # Filtra apenas os nós do tipo 'host'
            print(f"  {node}: {data.get('ip')}")

def menu_interativo(G):
    while True:
        comando = input("\nDigite um comando (ping <IP>, tabelas, sair): ").strip().lower()
        
        if comando.startswith("ping"):
            _, destino_ip = comando.split(maxsplit=1)
            ping_terminal(G, destino_ip)
        elif comando == "tabelas":
            mostrar_tabelas_roteamento()
        elif comando == "sair":
            print("Encerrando o programa...")
            plt.close()  # Fecha a janela do gráfico
            break
        else:
            print("Comando inválido. Tente novamente.")

def ping_terminal(G, destino_ip):
    origem = list(G.nodes())[0]  # Assume o primeiro nó como origem
    destino = None

    # Verifica se o IP de destino existe no grafo
    for node, data in G.nodes(data=True):
        if data.get('ip') == destino_ip:
            destino = node
            break

    if not destino:
        print(f"Host {destino_ip} não encontrado na rede.")
        return

    print(f"Disparando ping em {destino_ip} com 32 bytes de dados:")

    pacotes_enviados = 4
    pacotes_recebidos = 0
    tempos = []

    for _ in range(pacotes_enviados):
        try:
            # Tenta encontrar o caminho mais curto entre origem e destino
            caminho = nx.shortest_path(G, source=origem, target=destino, weight='weight')
            # Calcula a latência total do caminho
            latencia_total = sum(G[u][v]['weight'] for u, v in zip(caminho[:-1], caminho[1:]))
            print(f"Resposta de {destino_ip}: bytes=32 tempo={latencia_total}ms TTL={random.randint(50, 128)}")
            pacotes_recebidos += 1
            tempos.append(latencia_total)
        except nx.NetworkXNoPath:
            print("Esgotado o tempo limite do pedido.")
        time.sleep(1)

    perda = ((pacotes_enviados - pacotes_recebidos) / pacotes_enviados) * 100
    print(f"\nEstatísticas do Ping para {destino_ip}:")
    print(f"    Pacotes: Enviados = {pacotes_enviados}, Recebidos = {pacotes_recebidos}, Perdidos = {pacotes_enviados - pacotes_recebidos} ({int(perda)}% de perda)")

    if tempos:
        print(f"Aproximar um número redondo de tempos em milissegundos:")
        print(f"    Mínimo = {min(tempos)}ms, Máximo = {max(tempos)}ms, Média = {sum(tempos)//len(tempos)}ms")

def traceroute(G, destino_ip, max_hops=30):
    try:
        destino_ip_obj = ipaddress.IPv4Address(destino_ip)
    except ValueError:
        print(f"Erro: O IP {destino_ip} não é um endereço IPv4 válido.")
        return

    origem = "Switch_Central"  # O tráfego sempre começa pelo switch central
    destino = None

    # Busca o destino no grafo
    for node, data in G.nodes(data=True):
        if data.get('ip') == destino_ip:
            destino = node
            break

    if not destino:
        print(f"Erro: O IP {destino_ip} não foi encontrado na rede.")
        return

    print(f"\nRastreando rota para {destino_ip} a partir de {origem}...\n")

    try:
        if not nx.has_path(G, source=origem, target=destino):
            print("Erro: Não há caminho entre a origem e o destino. Verifique a conectividade.")
            return

        caminho = nx.shortest_path(G, source=origem, target=destino, weight='weight')
        print("Caminho encontrado:", caminho)
        total_saltos = min(len(caminho), max_hops)

        for i in range(total_saltos):
            nodo_atual = caminho[i]
            latencia = sum(G[u][v]['weight'] for u, v in zip(caminho[:i], caminho[1:i+1])) if i > 0 else 0
            ttl = max_hops - i  
            
            print(f"{i+1}\t{G.nodes[nodo_atual].get('ip', 'Desconhecido')}\t{latencia}ms\tTTL={ttl}")
            time.sleep(0.5)
    
    except nx.NetworkXNoPath:
        print("Erro: Não há caminho entre a origem e o destino. Verifique a conectividade.")

    print("\nRastreamento concluído.")


def plotar_rede():
    G = nx.Graph()
    
    # Adicionando nós
    for nome, ip in {**switch_central, **switches_agregacao, **switches_borda}.items():
        G.add_node(nome, type='dispositivo', ip=ip)
    
    for i, (key, host_list) in enumerate(hosts.items()):
        for j, host in enumerate(host_list):
            G.add_node(f"Host_{key}_{j+1}", type='host', ip=str(host))
    
    # Conexões entre dispositivos
    conexoes = [
        ("Switch_Central", "Switch_A1"),
        ("Switch_Central", "Switch_A2"),
        ("Switch_A1", "Switch_B1"),
        ("Switch_A1", "Switch_B2"),
        ("Switch_A1", "Switch_B3"),
        ("Switch_A1", "Switch_B4"),
        ("Switch_A2", "Switch_B5"),
        ("Switch_A2", "Switch_B6"),
        ("Switch_A2", "Switch_B7"),
        ("Switch_A2", "Switch_B8")
    ]
    
    for key, host_list in hosts.items():
        switch_borda = key.replace('hosts_e', 'Switch_B')
        for j in range(len(host_list)):
            conexoes.append((f"Host_{key}_{j+1}", switch_borda))
    
    # Adicionando arestas com latência simulada
    for origem, destino in conexoes:
        latencia = simular_ping()
        G.add_edge(origem, destino, weight=latencia)
    
    # Verifica se o grafo está conectado
    if not nx.is_connected(G):
        print("Aviso: O grafo não está completamente conectado. Alguns hosts podem ser inalcançáveis.")
    
    # Definir cores e tamanhos dos nós
    node_colors = ['orange' if G.nodes[n]['type'] == 'dispositivo' else 'lightblue' for n in G.nodes]
    node_sizes = [1000 if G.nodes[n]['type'] == 'dispositivo' else 500 for n in G.nodes]
    
    # Layout e visualização
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors, font_size=8, edge_color='gray')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
    plt.title("Topologia da Rede com Latência do Ping")
    plt.show(block=False)
    plt.pause(0.1)

    return G


def menu_interativo(G):
    while True:
        comando = input("\nDigite um comando (ping <IP>, tabelas, sair, traceroute): ").strip().lower()
        
        if comando.startswith("ping"):
            _, destino_ip = comando.split(maxsplit=1)
            ping_terminal(G, destino_ip)
        elif comando == "tabelas":
            mostrar_tabelas_roteamento(G)
        elif comando == "sair":
            print("Encerrando o programa...")
            plt.close()  # Fecha a janela do gráfico
            break
        elif comando.startswith("traceroute"):
            _, destino_ip = comando.split(maxsplit=1)
            traceroute(G, destino_ip)
        else:
            print("Comando inválido. Tente novamente.")

if __name__ == "_main_":
    G = plotar_rede()
    menu_interativo(G)
