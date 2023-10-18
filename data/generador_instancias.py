import random
import sys

def generar_instancia(numero_ordenes, numero_trabajadores, numero_conflicto_trabajadores, numero_ordenes_correlativas,
                    numero_ordenes_conflictivas, numero_ordenes_repetitivas, nombre_archivo):
    '''
    La función generar_ordenes crea un archivo de texto que simula un conjunto de datos de un sistema de gestión de órdenes. 
    Este archivo incluye información sobre el número de trabajadores, el número de órdenes, detalles de las órdenes 
    (como valores y asignaciones de trabajadores), relaciones de conflictos entre trabajadores, órdenes correlativas, 
    órdenes conflictivas y órdenes repetitivas. La función utiliza valores aleatorios para simular datos realistas y 
    los escribe en un formato legible en el archivo especificado.
    '''

    
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(str(numero_trabajadores)+'\n')
        archivo.write(str(numero_ordenes)+'\n')
        #ordenes
        for i in range(numero_ordenes):
            valor = random.randint(3000, 10000)
            trabajadores = random.randint(1, 5)
            linea = f"{i} {valor} {trabajadores}\n"
            archivo.write(linea)
        #cantidad trabajadores conflictivos
        archivo.write(str(numero_conflicto_trabajadores)+'\n')
        for i in range(numero_conflicto_trabajadores):
            valor1 = random.randint(0, numero_trabajadores-1)
            valor2 = random.randint(0, numero_trabajadores-1)
            while valor1 == valor2:
                valor1 = random.randint(0, numero_trabajadores-1)
                valor2 = random.randint(0, numero_trabajadores-1)

            linea = f"{valor1} {valor2}\n"
            archivo.write(linea)
        #cantidad ordenes correlativas
        archivo.write(str(numero_ordenes_correlativas)+'\n')
        for i in range(numero_ordenes_correlativas):
            valor1 = random.randint(0, numero_ordenes-1)
            valor2 = random.randint(0, numero_ordenes-1)
            while valor1 == valor2:
                valor1 = random.randint(0, numero_ordenes-1)
                valor2 = random.randint(0, numero_ordenes-1)

            linea = f"{valor1} {valor2}\n"
            archivo.write(linea)
        #cantidad ordenes conflictivas
        archivo.write(str(numero_ordenes_conflictivas)+'\n')
        for i in range(numero_ordenes_conflictivas):
            valor1 = random.randint(0, numero_ordenes-1)
            valor2 = random.randint(0, numero_ordenes-1)
            while valor1 == valor2:
                valor1 = random.randint(0, numero_ordenes-1)
                valor2 = random.randint(0, numero_ordenes-1)
            linea = f"{valor1} {valor2}\n"
            archivo.write(linea)
        #cantidad ordenes repetitivas
        archivo.write(str(numero_ordenes_repetitivas)+'\n')
        for i in range(numero_ordenes_repetitivas):
            valor1 = random.randint(0, numero_ordenes-1)
            valor2 = random.randint(0, numero_ordenes-1)
            while valor1 == valor2:
                valor1 = random.randint(0, numero_ordenes-1)
                valor2 = random.randint(0, numero_ordenes-1)
            linea = f"{valor1} {valor2}\n"
            archivo.write(linea)
        print('Se ha generado la instancia correctamente')

if __name__ == '__main__':
    if len(sys.argv) != 8:
        print("Usage: python generador_ordenes.py <numero_ordenes> <numero_trabajadores> <numero_conflicto_trabajadores> <numero_ordenes_correlativas> <numero_ordenes_conflictivas> <numero_ordenes_repetitivas> <nombre_archivo>")
    else:
        numero_ordenes = int(sys.argv[1])
        numero_trabajadores = int(sys.argv[2])
        numero_conflicto_trabajadores = int(sys.argv[3])
        numero_ordenes_correlativas = int(sys.argv[4])
        numero_ordenes_conflictivas = int(sys.argv[5])
        numero_ordenes_repetitivas = int(sys.argv[6])
        nombre_archivo = sys.argv[7]
        generar_instancia(numero_ordenes, numero_trabajadores, numero_conflicto_trabajadores, numero_ordenes_correlativas,
                        numero_ordenes_conflictivas, numero_ordenes_repetitivas, nombre_archivo)
