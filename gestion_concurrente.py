from datos import STOCK_INICIAL, NUM_CAJAS, PEDIDOS

import threading
import time

hilos = []

inventario = STOCK_INICIAL
pedidos_cajas = PEDIDOS


def inventario_cajas(pedidos_cajas):
    for pedidos in pedidos_cajas:
        nombre_producto = pedidos[1]
        cantidad_producto = pedidos[2]
        

        print("\nProducto:", nombre_producto)
        print("Cantidad :", cantidad_producto)


        # seccion crítica explicar en el readme
        stock = inventario[nombre_producto]
        print("stock:", stock)
        if stock >= cantidad_producto:
            inventario[nombre_producto] -= cantidad_producto
            print("\nUnidades descontadas correctamente")
        else:
            print("\nNo hay suficientes unidades")



if __name__ == "__main__":
    for i in range(NUM_CAJAS):

        pedidos_caja = pedidos_cajas[i::NUM_CAJAS]

        hilo = threading.Thread(
            target=inventario_cajas,
            args=(pedidos_caja,)
        )
        hilos.append(hilo)
        hilo.start()

    for i in hilos:
        i.join()

    print("\nInventario final -> ", inventario)
