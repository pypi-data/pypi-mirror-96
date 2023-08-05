Queuetools Async
===============

Herramientas para usar colas async.

- /coro/ send_async_queue(queue, value)
- /coro gen/ read_async_queue(queue)

Para enviar datos se debe usar await send----

Para recibir es una async generador, por lo que se recomienda usar en un /async for/

Clase Channel(síncronico)
============

Prove un canal de comunicación entre partes con colas direccionales

Clase AsyncChannel(asincrónico)
=================

Provee un canal de comunicación asíncrona, con colas direccionales.