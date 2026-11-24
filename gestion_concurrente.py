from datos import STOCK_INICIAL, NUM_CAJAS, PEDIDOS, NUM_TERMINALES, REPOSICIONES, NUM_REVISORES, TIEMPO_COBRO, TIEMPO_REPOSICION, CANCELACIONES

import threading
import time


class GestorInventario:
    def __init__(self):
        self.inventario = STOCK_INICIAL.copy()
        self.lock = threading.RLock()
        self.condicion = threading.Condition(self.lock)

        self.pedidos = {}

        for pedido in PEDIDOS:
            id_pedido = pedido[0]

            self.pedidos[id_pedido] = {
                "estado": "PENDIENTE",
                "producto": pedido[1],
                "unidades": pedido[2]
            }

    def consultar_stock(self, nombre_producto):
        with self.lock:
            return self.inventario[nombre_producto]

    def cambiar_estado(self, id_pedido, estado):
        with self.lock:
            self.pedidos[id_pedido]["estado"] = estado

    def descontar_stock(self, id_pedido, nombre_producto, cantidad_producto):
        with self.condicion:
            while self.inventario[nombre_producto] < cantidad_producto:

                if self.pedidos[id_pedido]["estado"] == "CANCELADO":
                    return False

                self.pedidos[id_pedido]["estado"] = "ESPERANDO_STOCK"

                self.condicion.wait()

            if self.pedidos[id_pedido]["estado"] == "CANCELADO":
                return False

            self.inventario[nombre_producto] -= cantidad_producto
            self.pedidos[id_pedido]["estado"] = "EN_COBRO"
            return True


    def reponer_stock(self, nombre_producto, cantidad_reponer):
        with self.condicion:
            self.inventario[nombre_producto] += cantidad_reponer
            self.condicion.notify_all()

    def cancelar_pedidos(self, id_pedido):
        with self.condicion:
            if id_pedido not in self.pedidos:
                return False

            estado = self.pedidos[id_pedido]["estado"]

            if estado not in ["PENDIENTE", "ESPERANDO_STOCK"]:
                return False

            self.pedidos[id_pedido]["estado"] = "CANCELADO"

            self.condicion.notify_all()
            return True

gestor = GestorInventario()
    
hilos = []

pedidos_cajas = PEDIDOS

# semaphore 

semaforo = threading.Semaphore(NUM_TERMINALES)

# barrera

barrera = threading.Barrier(NUM_REVISORES)


def inventario_cajas(pedidos_cajas, num_caja):
    for pedidos in pedidos_cajas:
        id_pedido = pedidos[0]
        nombre_producto = pedidos[1]
        cantidad_producto = pedidos[2]

        print("\nProducto:", nombre_producto)
        print("Cantidad :", cantidad_producto)

        with semaforo:
            print(f"\nObteniendo caja {num_caja}")

            resultado = gestor.descontar_stock(
                id_pedido, nombre_producto, cantidad_producto
            )

            if not resultado:
                continue

            time.sleep(TIEMPO_COBRO)

            gestor.cambiar_estado(id_pedido, "COMPLETADO")

            print(f"\nCaja {num_caja} liberada")


aceptadas = 0
rechazadas = 0


def procesar_cancelaciones(inicio):
    global aceptadas, rechazadas

    for cancelacion in CANCELACIONES:
        id_solicitud = cancelacion[0]
        id_pedido = cancelacion[1]
        segundo = cancelacion[2]

        tiempo_espera = segundo - (time.perf_counter() - inicio)

        if tiempo_espera > 0:
            time.sleep(tiempo_espera)

        resultado = gestor.cancelar_pedidos(id_pedido)

        if resultado:
            aceptadas += 1
            print(f"Solicitud {id_solicitud} -> pedido {id_pedido} cancelado")
        else:
            rechazadas += 1
            print(f"Solicitud {id_solicitud} -> pedido {id_pedido} rechazado")



def reposicion():
    for reponer in REPOSICIONES:
        time.sleep(TIEMPO_REPOSICION)


        nombre_producto = reponer[1]
        cantidad_reponer = reponer[2]

        gestor.reponer_stock(nombre_producto, cantidad_reponer)

        print(f"\nReposicion de {nombre_producto}")
        print(f"Se añadieron -> {cantidad_reponer}")


def revisar_inventario(productos, num_revisor):
    print(f"Revisor {num_revisor} empieza")

    for producto in productos:
        stock = gestor.consultar_stock(producto)
        print(f"Revisor {num_revisor} -> {producto}: {stock} unidades")
    barrera.wait()

    print(f"Revisor {num_revisor} ha finalizado")
    

if __name__ == "__main__":

    inicio = time.perf_counter()

    hilo_cancelaciones = threading.Thread(
        target=procesar_cancelaciones,
        args=(inicio,)
    )

    hilo_cancelaciones.start()

    for i in range(NUM_CAJAS):

        pedidos_caja = pedidos_cajas[i::NUM_CAJAS]

        hilo = threading.Thread(
            target=inventario_cajas,
            args=(pedidos_caja, i + 1)
        )
        hilos.append(hilo)
        hilo.start()

    hilo_reposicion = threading.Thread(
        target=reposicion
    )

    hilo_reposicion.start()

    
    for i in hilos:
        i.join()

    hilo_reposicion.join()

    productos = list(gestor.inventario.keys())

    hilos_revisores = []

    for i in range(NUM_REVISORES):
        productos_revisor = productos[i::NUM_REVISORES]

        hilo = threading.Thread(
            target=revisar_inventario,
            args=(productos_revisor, i + 1)
        )

        hilos_revisores.append(hilo)
        hilo.start()

    for hilo in hilos_revisores:
        hilo.join()

    hilo_cancelaciones.join()

    print("\nEstados finales de los pedidos:")

    for id_pedido, datos_pedido in gestor.pedidos.items():
        print(id_pedido, "->", datos_pedido["estado"])


    print("\nInventario final -> ", gestor.inventario)

print("\n========== RESUMEN FINAL ==========")

completados = 0
cancelados = 0
pendientes = 0
esperando = 0
en_cobro = 0

for datos_pedido in gestor.pedidos.values():
    estado = datos_pedido["estado"]

    if estado == "COMPLETADO":
        completados += 1
    elif estado == "CANCELADO":
        cancelados += 1
    elif estado == "PENDIENTE":
        pendientes += 1
    elif estado == "ESPERANDO_STOCK":
        esperando += 1
    elif estado == "EN_COBRO":
        en_cobro += 1

print("Pedidos completados:", completados)
print("Pedidos cancelados:", cancelados)
print("Pedidos pendientes:", pendientes)
print("Pedidos esperando stock:", esperando)
print("Pedidos en cobro:", en_cobro)

print("Solicitudes de cancelación aceptadas:", aceptadas)
print("Solicitudes de cancelación rechazadas:", rechazadas)

print("===================================")