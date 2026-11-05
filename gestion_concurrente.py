from datos import STOCK_INICIAL, NUM_CAJAS, PEDIDOS, NUM_TERMINALES, REPOSICIONES, NUM_REVISORES

import threading
import time

hilos = []

inventario = STOCK_INICIAL.copy()
pedidos_cajas = PEDIDOS

# lock que evita cambios simultaneos 

lock = threading.Lock()

# semaphore 

semaforo = threading.Semaphore(NUM_TERMINALES)

# condicion para las reposiciones 

condicion = threading.Condition(lock)

# barrera

barrera = threading.Barrier(NUM_REVISORES)


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

            with condicion:
                stock = inventario[nombre_producto]
                print("stock:", stock)

                while inventario[nombre_producto] < cantidad_producto:
                    print(f"Caja {num_caja} esperando reposición de {nombre_producto}")
                    condicion.wait()
                print(f"Caja {num_caja} continúa con el pedido de {nombre_producto}")

                inventario[nombre_producto] -= cantidad_producto
                print("\nUnidades descontadas correctamente")

                    
            print(f"\nCaja {num_caja} liberada")


def reposicion():
    for reponer in REPOSICIONES:
        time.sleep(2)


        nombre_producto = reponer[1]
        cantidad_reponer = reponer[2]

        with condicion:
            inventario[nombre_producto] += cantidad_reponer

            print(f"\nReposicion de {nombre_producto}")
            print(f"Se añadieron -> {cantidad_reponer}")

            condicion.notify_all()


def revisar_inventario(productos, num_revisor):
    print(f"Revisor {num_revisor} empieza")

    for producto in productos:
        print(f"Revisor {num_revisor} -> {producto}: {inventario[producto]} unidades")

    print(f"Revisor {num_revisor} ha finalizado")
    

if __name__ == "__main__":
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

    productos = list(inventario.keys())

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

    print("\nInventario final -> ", inventario)
