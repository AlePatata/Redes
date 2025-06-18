
### Funciones Auxiliaresss

def format(i):
  return str(i).zfill(3).encode()

def estaEnVentana(begin, n, win):
  return (n - begin + 1000) % 1000 < win

def siguienteAck(n, s=1):
  return (n+s)%1000

def distanciaBetween(a,b):
  return (b - a + 1000)%1000