from datos import STOCK_INICIAL, NUM_CAJAS, PEDIDOS, NUM_TERMINALES, REPOSICIONES, NUM_REVISORES, CANCELACIONES

import threading
import time


class GestorInventario:
    def __init__(self):
        self.inventario = STOCK_INICIAL.copy()
        self.lock = threading.RLock()
        self.condicion = threading.Condition(self.lock)

    def consultar_stock(self, nombre_producto):
        with self.lock:
            return self.inventario[nombre_producto]

    def descontar_stock(self, nombre_producto, cantidad_producto):
        with self.condicion:
            while self.consultar_stock(nombre_producto) < cantidad_producto:
                self.condicion.wait()

            self.inventario[nombre_producto] -= cantidad_producto

    def reponer_stock(self, nombre_producto, cantidad_reponer):
        with self.condicion:
            self.inventario[nombre_producto] += cantidad_reponer
            self.condicion.notify_all()

gestor = GestorInventario()
    
hilos = []

pedidos_cajas = PEDIDOS
estado = pedidos_cajas[3]

# cancelaciones

cancelar_pedido = CANCELACIONES
pedidos_cancelados = 0
pedidos_vendidos = 0
pedidos_rechazados = 0

# semaphore 

semaforo = threading.Semaphore(NUM_TERMINALES)

# barrera

barrera = threading.Barrier(NUM_REVISORES)


def inventario_cajas(pedidos_cajas, num_caja):
    for pedidos in pedidos_cajas:
        nombre_producto = pedidos[1]
        cantidad_producto = pedidos[2]
        estado = pedidos[3]


        print("\nProducto:", nombre_producto)
        print("Cantidad :", cantidad_producto)

        with semaforo:
            print(f"\nObteniendo caja {num_caja}")
            time.sleep(1)

        stock = gestor.consultar_stock(nombre_producto)
        print("stock:", stock)

        if stock < cantidad_producto:
            print(f"Caja {num_caja} esperando reposición de {nombre_producto}")

        gestor.descontar_stock(nombre_producto, cantidad_producto)


        print(f"Caja {num_caja} continúa con el pedido de {nombre_producto}")
        print("\nUnidades descontadas correctamente")

        print(f"\nCaja {num_caja} liberada")
        if estado == "pendiente":
            estado = "vendido"

        print(f"estado -> {estado}")



def cancelaciones(cancelar_pedido):
    for cancelacion in cancelar_pedido:
        time.sleep(cancelacion[2])
        nombre_cancelacion = cancelacion[0]
        nombre_pedido = cancelacion[1]

        if estado == "pendiente":
            estado = "rechazado"
            
        print(f"estado -> {estado}")

        print(f"{nombre_cancelacion} ha cancelado el pedido -> {nombre_pedido}")






def reposicion():
    for reponer in REPOSICIONES:
        time.sleep(2)


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

    hilo_cancelar = threading.Thread(
        target=cancelaciones,
        args=(cancelar_pedido,)
    )
    hilo_cancelar.start()

    for i in range(NUM_CAJAS):

        pedidos_caja = pedidos_cajas[i::NUM_CAJAS]

        hilo = threading.Thread(
            target=inventario_cajas,
            args=(pedidos_caja, i + 1)
        )
        hilos.append(hilo)
        hilo.start()

        if estado == "vendido":
            pedidos_vendidos += 1
            print(f"Productos vendidos -> {estado}")

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

    hilo_cancelar.join()

    print("\nInventario final -> ", gestor.inventario)

    print(f"\nResumen cancelaciones")
    print(f"Pedidos cancelados -> {pedidos_cancelados}")
    print(f"Pedidos vendidos -> {pedidos_vendidos}")
    print(f"Solicitudes rechazadas -> {pedidos_rechazados}")
