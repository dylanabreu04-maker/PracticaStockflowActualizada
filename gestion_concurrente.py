from datos import STOCK_INICIAL, NUM_CAJAS, PEDIDOS, NUM_TERMINALES

import threading
import time

hilos = []

inventario = STOCK_INICIAL.copy()
pedidos_cajas = PEDIDOS

# lock que evita cambios simultaneos 

lock = threading.Lock()


# semaphore 

semaforo = threading.Semaphore(NUM_TERMINALES)


def inventario_cajas(pedidos_cajas, num_caja):
    for pedidos in pedidos_cajas:
        nombre_producto = pedidos[1]
        cantidad_producto = pedidos[2]
        

        print("\nProducto:", nombre_producto)
        print("Cantidad :", cantidad_producto)

        with semaforo:
            print(f"\nObteniendo caja {num_caja}")
            time.sleep(1)

        # seccion crítica explicar en el readme
            with lock:
                stock = inventario[nombre_producto]
                print("stock:", stock)
                if stock >= cantidad_producto:
                    inventario[nombre_producto] -= cantidad_producto
                    print("\nUnidades descontadas correctamente")
                else:
                    print("\nNo hay suficientes unidades")

            print(f"\nCaja {num_caja} liberada")



if __name__ == "__main__":
    for i in range(NUM_CAJAS):

        pedidos_caja = pedidos_cajas[i::NUM_CAJAS]

        hilo = threading.Thread(
            target=inventario_cajas,
            args=(pedidos_caja, i + 1)
        )
        hilos.append(hilo)
        hilo.start()

    for i in hilos:
        i.join()

    print("\nInventario final -> ", inventario)
