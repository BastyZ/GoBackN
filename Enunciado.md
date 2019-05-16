# Cliente  Go-Back-N
El siguiente es el enunciado de la tarea pasado de pdf a Markdown.

## Objetivos
La ﬁnalidad de esta tarea es que construyan un servicio de transporte conﬁable sobre UDP. **Está estrictamente prohibido
 usar sockets TCP**. 
 
 Se les entrega un servidor Go-Back-N (construido usando por supuesto UDP), que recibe paquetes de un archivo y lo va 
 reconstruyendo (piensen que su objetivo es ser un servidor para respaldo de archivos). Este servidor funciona 
 correctamente: recibe los paquetes de a uno y les envía ACKs según los paquetes van llegando. 
 Lo que no funciona tan bien es la conexión: los paquetes pueden perderse, desordenarse o corromperse, además de que el
  RTT no es para nada constante. 
  
 La tarea de ustedes es crear un cliente que le envíe las cosas al servidor, asegurándose de que lleguen como 
 corresponde (a través de un sistema de ACKs y retransmisiones).

## Servidor entregado
El servidor entregado viene como un ejecutable (no está permitido ver su código fuente, deben trabajar sin conocerlo).
Dentro del directorio *server* entregado junto con el enunciado viene un ejecutable server. El servidor recibe los
 siguientes parámetros para comenzar a trabajar:
1. Número máximo de números de secuencia en número de caracteres: por ejemplo, 2, son 100 números distintos (0-99); 
3 son 1.000 (0-999). 
2. Puerto de entrada (por el cual se recibirá los paquetes que ustedes le manden). 
3. Puerto de salida (por el cual les mandará los ACKs). 
4. IPdelreceptor (en general, pueden dejar esto como localhost, pero si lo desean pueden probar en dos computadores).

##Un ejemplo de ejecución del servidor:
```bash
$ .\server 2 8989 9090 127.0.0.1
```
Esto levanta un servidor que espera números de secuencia del 0 al 99, que recibe datos por el puerto 8989 y manda ACKs
 por el puerto 9090 a localhost (127.0.0.1). 
 
####Puntos importantes:
1. El servidor es mono-cliente, si más de un cliente le envía información no hace diferencia entre ellos. 
2. Por simplicidad, vamos a trabajar usando strings. 
3. El servidor escribe en pantalla información relevante, para que puedan hacer debugging de lo que ocurre con su cliente.

El servidor recibe los paquetes enviados por ustedes a través del socket y los parsea como sigue:

- Se separan header y data. El tamaño del header corresponde a N (donde N es el número seteado como número de caracteres 
de los números de secuencias) más el tamaño del checksum del paquete 
- Los primeros N caracteres del header se extraen para obtener el número de secuencia y procesarlo. Si el número de 
secuencia es no numérico el servidor solamente lo desechará, imprimiendo “Invalid packet”.
- Los últimos caracteres corresponden al checksum del paquete. Para esta tarea trabajaremos con md5, que siempre genera 
secuencias de 128 bits, por lo que son 32 caracteres de checksum. 
- El resto del paquete corresponde a la data que ustedes envíen. Esta data viene representada como un string, pero el
 server la transforma en bytes y la escribe en un archivo
 
El servidor recibe sus paquetes en orden, partiendo desde el número de secuencia 0 (no hay handshake en esta tarea) 
y sigue las reglas normales de un receptor en Go-Back-N:

1. Cuando el receptor recibe un paquete lo primero que hace es chequear el checksum. Si el checksum de la data (no del 
paquete completo) no calza, el paquete no es considerado y se descarta (no se envía ACK).
2. Si el paquete pasa la prueba del checksum, se chequea si el número de secuencia corresponde al esperado o no. 
Si calza, se acepta el paquete y se manda un ACK para él; si no calza, se rechaza el paquete (no se guarda su 
información) y se manda un ACK para el último paquete recibido.
3. Cuando el servidor recibe un paquete vacío (sin número de secuencia, checksum o data), asume que el server ha 
terminado de enviar data y cierra el socket. Para cerrar el servidor, se usa Control+C. Solo deben mandar este paquete 
vacío después de asegurarse que toda la información llegue bien, es decir, el último paquete ha recibido su ACK. Si 
envían anticipadamente este paquete, el servidor dejará de recibir paquetes, solo procesando aquellos ya recibidos.

## Implementación pedida
Se les pide implementar un cliente que se comunique de manera conﬁable con el servidor entregado. El cliente debería 
recibir los siguientes parámetros (ya sea a través de línea de comando, archivo de conﬁguración o una combinación de 
ambos):

1. IP del servidor al cual enviar los archivos.
2. Nombre del archivo a enviar.
3. Tamaño (en número de paquetes) de la ventana. Esta ventana será constante (no se pide realizar control de ﬂujo o 
de congestión).
4. Tamaño de los paquetes a enviar.
5. Número máximo de números de secuencia.
6. Puertos para: (1) enviar información, (2) recibir los ACKs.

*Es importante comentar que el número máximo de números de secuencia debe ser el mismo entre cliente y servidor, 
esta es una restricción que siempre se cumplirá cuando corran su tarea.*

El valor del timeout deberán calcularlo usando el algoritmo de Karn, tomando como valor inicial 1 segundo.

El primer paso es crear un cliente con dos hilos de ejecución (ya sea threads o procesos), uno para enviar la data 
(Proceso de envío) y otro para recibir los potenciales ACK del servidor (Proceso de recepción). 

### Proceso de envío
Los puntos que debe cumplir esta parte de su tarea son:

1. Inicializar una ventana de envío, con las variables relevantes: inicio de la ventana (inicialmente en 0), último paquete enviado y último paquete ackeado. Es importante que consideren que el número de paquetes de la ventana no puede superar el límite entregado. Además de la ventana de envío se les aconseja guardar una ventana “paralela” con los tiempos de envío de los paquetes y si han sido retransmitidos o no (para el cálculo de los timeouts). 
2. Leer la data del archivo elegido, formatear a string y dividirla en trozos del tamaño seleccionado. Tomar los trozos y mientras haya espacio en la ventana:

    a) Determinar el número de secuencia de este paquete.
    **Importante**: Los números de secuencia siempre se trabajarán usando el número máximo de caracteres; por ejemplo, si los números de secuencia son de 3 caracteres y deben enviar el paquete 9, su número de secuencia debe mandarse como 009 o el servidor lo interpretará como un paquete corrupto.

    b)Calcular el checksum del trozo de data (solamente data) a enviar (md5 en este caso).
    
    c) Incluir los caracteres iniciales del header (número de secuencia y checksum).
    
    d) Guardar este paquete en la ventana.
    
    e) Guardar el tiempo de envío del paquete en la ventana.
    
    f) Enviar el paquete por el socket.
3. Cada vez que se envíe el paquete cuyo número de secuencia sea igual al inicio de la ventana, se inicia un timer (timeout). Si se llega a este timeout, reenviar todo lo que esté en la ventana. Cuando se reenvían los paquetes, no olvidar guardar esta información junto con el nuevo tiempo de envío en la ventana paralela, de tal manera de no considerar los ACKs de estos paquetes en el cálculo del timeout.

### Proceso de recepción
Los puntos que debe cumplir esta parte de su tarea son:
1. Recibir ACKs. Los ACKs son básicamente iguales a los paquetes que ustedes envían, pero sin data: primeros N 
caracteres son el número de secuencia(donde N es el número de caracteres seteados para esto),seguido de 32 caracteres de 
checksum. Deben validar este checksum: calculen el checksum sobre el número de secuencia como string y compárarenlo 
con el número que va en el paquete; si son iguales, el ACK es válido y se continúa procesando, de lo contrario se 
descarta.
2. Marcar paquetes como recibidos. Cuando se recibe un ACK se revisa la ventana y se marcan como recibidos todos los paquetes con número de secuencia menor o igual a la secuencia de este ACK. Cuando se marca como recibido el primer paquete de la ventana, este timer desaparece y se crea uno para el primer paquete de la ventana (si es que hay).
3. Actualizar la ventana. Cambiar el valor de las variables inicio de ventana y último ackeado para representar la nueva situación. Esto hará que potencialmente el proceso de envío pueda mandar más información.
4. Cálculo del timeout. Cada vez que reciban un ACK para un paquete deben revisar si ha sido retransmitido o no; un ACK para un paquete retransmitido no se puede usar para el cálculo del timeout. El cálculo del timeout se realiza utilizando la fórmula de Karn vista en clases (ir a clase 7-8, a partir de la diapo 44). Este timeout se utiliza desde este punto en adelante, es decir, la próxima vez que requieran setear un timer, este nuevo valor de timeout se utilizará

## Nota extremadamente importante
No asuman de ninguna manera que sus paquetes llegan al server (se pueden perder), que llegan bien (sin corromper) o que llegan de inmediato (puede haber cierto atraso)

Si ustedes le mandan un paquete al server, no esperen recibir siempre un ACK para él. Tienen que estar preparados para este caso. Además, pueden recibir un ACK corrupto (checksum no calza con el número de secuencia), lo que hace que la información del ACK sea inútil.

Es extremadamente importante que prueben que su tarea funcione sin importar estas cosas. Para probar su tarea bajo condiciones no ideales, revisar la utilidad netem de Linux (más sobre ella en auxiliar)

## Informe
Detalle importante: deben entregar un README explicando como correr su tarea,yaclarandosussupuestos.Selesrepitesu tarea debe poder correrse sin complicaciones por parte del corrector. Por favor consideren que mientras mejor documentada su tarea, más fácil su evaluación y menos problemas tendrán.

## Restricciones
Ustedes deben implementar lo pedido en uno de los siguientes lenguajes de programación: Java, C, C++ o Python.

La posibilidad de utilizar otros lenguajes no está cerrada, pero debe conversarse con la auxiliar previamente (básicamente para asegurarse de que su tarea sea revisable).

Cualquier duda o pregunta o reporte de bugs, dirigirse al foro de U-cursos.

## Evaluación
Esta tarea será evaluada tomando en cuenta el funcionamiento de su cliente, siguiendo los siguientes puntos:

1. Son capaces de hacer llegar información al servidor
2. Implementaron un Go-Back-N, no se aceptarán implementaciones de Stop-And-Wait (mandar paquetes de a uno)
3. Son capaces de trabajar con pérdida, atraso y corrupción de paquetes, haciendo llegar la data íntegra a destino. Siempre chequear que el archivo en destino sea idéntico a lo enviado.
