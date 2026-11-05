# StockFlow – Sincronización de hilos

## 1. Descripción general

StockFlow es una aplicación desarrollada en Python que simula el funcionamiento de una tienda. Varias cajas procesan pedidos al mismo tiempo mientras el almacén realiza reposiciones de productos.

El objetivo de la práctica es estudiar los problemas que aparecen cuando varios hilos acceden a un mismo inventario y solucionarlos utilizando diferentes mecanismos de sincronización.

## 2. Cómo ejecutar la aplicación

Para ejecutar el programa, es necesario tener Python instalado y disponer de los archivos del proyecto.

Desde la terminal, situarse en la carpeta del proyecto y ejecutar:


python gestion_concurrente.py


## 3. Estructura de archivos

- datos.py: contiene los datos iniciales de la simulación, como el inventario, los pedidos, las reposiciones y el número de cajas, terminales y revisores.
- gestion_concurrente.py: contiene la lógica de la aplicación y los mecanismos de sincronización.
- README.md: contiene la documentación del proyecto.

## 4. Condición de carrera inicial

En la primera fase, varias cajas podían consultar y modificar el stock de un mismo producto al mismo tiempo.

El problema se encontraba en la comprobación y el descuento del inventario. Una caja podía consultar que quedaban unidades suficientes y, antes de descontarlas, otra caja podía realizar la misma comprobación.

Esto podía provocar que varias cajas vendieran unidades que realmente no estaban disponibles, generando resultados incoherentes.

La sección crítica era la parte del código encargada de comprobar el stock y descontar las unidades.

Para solucionar este problema se utilizó un mecanismo de exclusión mutua.

## 5. Mecanismos de sincronización utilizados

### Lock

Se utilizó para proteger el inventario y evitar que varios hilos modificaran el stock al mismo tiempo.

La comprobación de las unidades disponibles y el descuento se realizan de forma protegida, evitando que dos cajas modifiquen simultáneamente el mismo stock.

### Semaphore

Se utilizó para limitar el número de cajas que pueden utilizar un terminal de cobro al mismo tiempo.

El número máximo de cajas que pueden utilizar los terminales se obtiene de NUM_TERMINALES.

Este mecanismo controla el acceso a los terminales, mientras que el bloqueo del inventario protege los datos compartidos.

### Condition

Se utilizó para gestionar las esperas cuando una caja intenta procesar un pedido y no existe stock suficiente.

La caja espera mediante wait() hasta que el almacén realiza una reposición.

Cuando se añade mercancía, se utiliza notify_all() para avisar a los hilos que están esperando. Después de despertarse, cada caja vuelve a comprobar si hay unidades suficientes antes de continuar.

Se utiliza un bucle while para comprobar de nuevo la condición, ya que recibir una notificación no garantiza que el stock siga siendo suficiente.

### Barrier

Se utilizó para sincronizar los hilos revisores durante el cierre del inventario.

Cada revisor comprueba una parte del catálogo y, cuando termina, llega al punto de sincronización mediante wait().

El cierre no continúa hasta que todos los revisores han llegado a la barrera. Después se muestra el resumen final del inventario.

### RLock

Se utilizó dentro de la clase GestorInventario para organizar las operaciones relacionadas con el inventario.

Es necesario porque la operación descontar_stock() llama a consultar_stock(), y ambas operaciones utilizan el mismo bloqueo.

Un Lock normal no permitiría que el mismo hilo adquiriese de nuevo el bloqueo que ya tiene adquirido, por lo que podría quedarse bloqueado.

RLock permite que el mismo hilo adquiera varias veces el mismo bloqueo y pueda completar ambas operaciones correctamente.

## 6. Prevención de deadlock

Un deadlock o interbloqueo puede producirse cuando varios hilos esperan recursos que están siendo utilizados por otros hilos y ninguno puede continuar.

Un posible ejemplo sería que una caja obtuviese primero el Semaphore y después intentase adquirir el bloqueo del inventario, mientras que otro hilo obtuviese primero el bloqueo del inventario y después intentase conseguir el Semaphore.

Si ambos recursos permaneciesen ocupados y cada hilo esperase el recurso que tiene el otro, se produciría un interbloqueo.

Para evitarlo, en esta aplicación se procura no adquirir ambos recursos de forma anidada. La caja libera el Semaphore antes de acceder al inventario. Además, las esperas y operaciones que no necesitan proteger los datos se realizan sin mantener bloqueos innecesariamente.

La operación wait() de Condition también libera temporalmente el bloqueo mientras el hilo espera, permitiendo que el almacén pueda realizar la reposición.

## 7. Pruebas realizadas

Se han realizado las siguientes comprobaciones:

- **Condición de carrera:** se ha comprobado como los numeros al finalizar todos los hilos el stock era negativo.
- **Lock:** se ha comprobado que la comprobación y el descuento del stock están protegidos.
- **Semaphore:** se ha comprobado que no se supera el número de terminales disponibles.
- **Condition:** se ha comprobado que una caja espera cuando no hay stock y continúa después de una reposición.
- **Barrier:** se ha comprobado que los revisores esperan hasta que todos terminan su comprobación.
- **Solución final:** se ha ejecutado varias veces para comprobar que no aparecen stocks negativos ni ventas incoherentes.


## 8. Git y desarrollo por fases

El proyecto se ha desarrollado utilizando Github y una estructura de ramas para cada fase realizada.

Se ha utilizado main para mantener las versiones estables y develop como rama de integración.

Las nuevas funcionalidades se han trabajado en ramas feature independientes, integrándolas posteriormente en develop.

Finalmente, la versión terminada se integra en main.