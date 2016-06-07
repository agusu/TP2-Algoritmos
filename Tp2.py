import csv

LISTA_OPCIONES = ['Inflación por supermercado',
                  'Inflación por producto',
                  'Inflación general promedio',
                  'Mejor precio para un producto',
                  'Salir']
INFLACION_POR_SUPERMERCADO = 1
INFLACION_POR_PRODUCTO = 2
INFLACION_GENERAL_PROMEDIO = 3
MEJOR_PRECIO_PRODUCTO = 4
CANT_OPCIONES = len(LISTA_OPCIONES)
AÑO = 2016


def main():
    """Inicia un programa con interfaz amigable para cálculos de inflación,
     entre otros, utilizando tres archivos csv."""
    try:
        datos, lista_registros_fallidos = cargar_datos_en_diccionario("precios.csv",
                                                                  "productos.csv",
                                                                  "supermercados.csv")
        imprimir_fallidos(lista_registros_fallidos)
        opcion = ""
    except IOError:
        print('Error fatal: corrobore el estado de los archivos de datos.')
        opcion = 5

    while opcion != 5:
        mostrar_menu()
        opcion = pedir_opcion()
        if opcion == INFLACION_POR_SUPERMERCADO:
            calcular_inflacion_por_supermercado(datos)
        elif opcion == INFLACION_POR_PRODUCTO:
            calcular_inflacion_por_producto(datos)
        elif opcion == INFLACION_GENERAL_PROMEDIO:
            calcular_inflacion_general(datos)
        elif opcion == MEJOR_PRECIO_PRODUCTO:
            calcular_mejor_precio(datos)
    print("Hasta luego.")


def calcular_inflacion_por_supermercado(datos):
    """Calcula la inflacion por supermercado en un periodo de fechas pedido al usuario y lo imprime"""
    print('Ingrese la fecha inicial y final del periodo a estudiar')
    fechas = (pedir_fecha(), pedir_fecha())
    inflacion = inflacion_por_supermercado(datos, fechas)
    mostrar_inflacion(inflacion)


def calcular_inflacion_por_producto(datos):
    """Calcula la inflacion de un producto en un periodo de fechas pedido al usuario y lo imprime"""
    try:
        producto = pedir_producto(datos)
        print('Ingrese la fecha inicial y final del periodo a estudiar')
        fechas = (pedir_fecha(), pedir_fecha())
        inflacion = calcular_inflacion(datos, producto,
                                       fechas)
        mostrar_inflacion(inflacion)
    except (TypeError, KeyError) as error:
        print(error)


def calcular_inflacion_general(datos):
    """Calcula el promedio de la inflacion general en un periodo de fechas pedido al usuario y la imprime"""
    print('Ingrese la fecha inicial y final del periodo a estudiar')
    fechas = (pedir_fecha(), pedir_fecha())
    inflacion_promedio = inflacion_general_promedio(datos, fechas)
    mostrar_inflacion_promedio(inflacion_promedio)


def calcular_mejor_precio(datos):
    """Calcula el mejor precio para un producto en un periodo de fechas pedido al usuario y lo imprime"""
    try:
        producto = pedir_producto(datos)
        fecha = pedir_fecha()
        supermercado, precio = mejor_precio_supermercado(datos, producto,
                                                         fecha)
        mostrar_mejor_precio(supermercado, precio)
    except TypeError:
        print("El producto no se vende en ninguno de los supermercados para esa fecha ")


# ---------------------------------------------------------------------
# |                    Cargado de datos en memoria                    |
# ---------------------------------------------------------------------

def cargar_datos_supermercado_en_diccionario(arch):
    """Ingresa como parametro la ruta de un archivo csv con 2 campos.
    Devuelve un diccionario con el primer campo del archivo como clave y el segundo como valor"""
    try:
        with open(arch, "r") as f_archivo:
            dicc = {}
            archivo_csv = csv.reader(f_archivo)
            next(archivo_csv)
            for clave, valor in archivo_csv:
                clave = int(clave)
                dicc[clave] = dicc.get(clave, "") + valor
        return dicc
    except IOError:
        raise IOError


def verificar_registro_principal(registro, encabezado):
    """Recibe una lista con la linea actual del archivo precio.csv y el encabezado del
    mismo archivo. Devuelve True si la linea esta bien cargada y False sino lo está"""
    try:

        if len(registro) == len(encabezado):
            if registro[0].isdigit() and registro[1].isdigit():
                float(registro[3])
                if len(registro[2]) == 6:
                    if es_año(registro[2][:4]) and es_mes(registro[2][4:]):
                        return True

        return False
    except TypeError:  # por si entra None o el precio no es numérico
        return False


def verificar_registro_secundario(registro, encabezado):
    """Recibe una lista con la linea actual del archivo productos.csv y el encabezado
     del mismo archivo. Devuelve True si la linea esta bien cargada y False si no lo está"""
    try:
        if len(registro) != len(encabezado):
            return False
        try:
            assert type(registro[1]) == str
        except AssertionError:
            return False
        return True
    except TypeError:  # por si entra None
        return False


def cargar_datos_en_diccionario(arch1, arch2, arch3):
    """Ingresa como parametros 3 archivos. Devuelve un diccionario con los datos
    de los archivos de la forma {PRODUCTO:{SUPERMERCADO:{FECHA:PRECIO}"""
    # abro el archivo de 4 campos y el de los producto.
    try:
        with open(arch1, "r") as principal, open(arch2, "r") as secundario:
            # cargo los datos del  archivo de los supermercados y lo meto en un diccionario.
            diccionario_sup = cargar_datos_supermercado_en_diccionario(arch3)
            datos_productos_csv = csv.reader(secundario)
            archivo_csv = csv.reader(principal)
            encabezado_principal = next(archivo_csv, None)
            encabezado_secundario = next(datos_productos_csv, None)
            registro_principal = next(archivo_csv, None)
            registro_secundario = next(datos_productos_csv, None)
            dicc_productos = {}
            lista_registros_fallidos = []
            # empieza corte de control por producto.
            # Mientras registro_principal y registro_secundario no sean None.
            while registro_principal and registro_secundario:
                while not verificar_registro_principal(registro_principal, encabezado_principal) \
                        and registro_principal:
                    lista_registros_fallidos.append(registro_principal)
                    registro_principal = next(archivo_csv, None)
                while not verificar_registro_secundario(registro_secundario, encabezado_secundario) \
                        and registro_secundario:
                    registro_secundario = next(datos_productos_csv, None)

                id_producto = int(registro_principal[1])
                dicc_supermercados = {}

                while registro_principal and id_producto == int(registro_principal[1]) \
                        and id_producto <= int(registro_secundario[0]):
                    # recorro archivo productos hasta encontrar el id producto
                    if int(registro_principal[1]) < int(registro_secundario[0]):
                        while not verificar_registro_principal(registro_principal,
                                                               encabezado_principal) \
                                and registro_principal:
                            lista_registros_fallidos.append(registro_principal)
                            registro_principal = next(archivo_csv, None)
                        id_producto = registro_principal[1]
                        continue

                    supermercado = int(registro_principal[0])
                    nom_supermercado = diccionario_sup.get(supermercado, "")
                    dicc_fechas = {}

                    while registro_principal and supermercado == int(registro_principal[0]):
                        dicc_fechas[registro_principal[2]] = float(registro_principal[3])
                        registro_principal = next(archivo_csv, None)
                        while not verificar_registro_principal(registro_principal,
                                                               encabezado_principal) \
                                and registro_principal:
                            lista_registros_fallidos.append(registro_principal)
                            registro_principal = next(archivo_csv, None)

                    dicc_supermercados[nom_supermercado] = dicc_fechas

                if dicc_supermercados != {}:  # si el diccionario está vacío, no lo guarda.
                    dicc_productos[registro_secundario[
                        1]] = dicc_supermercados  # La clave va a ser el nombre del producto
                registro_secundario = next(datos_productos_csv, None)
        return dicc_productos, lista_registros_fallidos
    except IOError:
        print("No se encontró el/los archivo/s. Verifique la existencia de los archivos:"
              "precios.csv"
              "productos.csv"
              "supermercados.csv")


# ---------------------------------------------------------------------
# |              Inflacion por Supermercado y Prodcuto                |
# ---------------------------------------------------------------------


def inflacion_por_supermercado(diccionario_datos, fechas):
    """Recibe como parametro un diccionario y una tupla de fechas.
    Devuelve la inflacion total de los supermercados en un diccionario"""
    inflacion_total = {}
    cantidad_de_productos = 1
    for producto in diccionario_datos.keys():
        inflacion = calcular_inflacion(diccionario_datos, producto, fechas)
        for supermercado, inflacion_producto in inflacion:
            if supermercado not in inflacion_total.keys():
                inflacion_total[supermercado] = [inflacion_producto, cantidad_de_productos]
                continue
            valor_anterior = inflacion_total.pop(supermercado)
            inflacion_total[supermercado] = inflacion_total.get(supermercado, []) + [
                valor_anterior[0] + inflacion_producto, valor_anterior[1] + 1]
    for supermercado, lista in inflacion_total.items():
        inflacion_total[supermercado] = lista[0] / lista[1]
    return inflacion_total.items()


def calcular_inflacion(diccionario_datos, producto, fechas):
    """Recibe como parametro un diccionario, una cadena y una tupla de fechas.
    Devuelve una lista de tuplas, donde cada tupla contiene el nombre del
    supermercado y su inflacion"""
    inflacion = []
    supermercado = diccionario_datos.get(producto, {})
    # asigna en la variable supermercado, un dicionario cuya clave
    # es el nombre del supermercado y el valor es otro diccionario de fechas
    for clave in supermercado:
        try:
            dicc_fechas = supermercado.get(clave, {})
            precioi = dicc_fechas.get(fechas[0], None)
            preciof = dicc_fechas.get(fechas[1], None)
            inflacion.append((clave, 100 * ((preciof - precioi) / precioi)))
        except TypeError:
            # Si el supermercado no tiene el producto para alguna de las fechas,
            # pasa al siguiente supermercado
            continue
    if inflacion:
        return inflacion
    return None


# ---------------------------------------------------------------------
# |                     Inflacion general promedio                    |
# ---------------------------------------------------------------------


def inflacion_general_promedio(diccionario_datos, fechas):
    """Recibe como parametro un diccionario y un rango de fechas.
    Devuelve la inflacion general promedio de todos los productos """
    inflacion_promedio = 0
    for producto in diccionario_datos.keys():
        inflacion = calcular_inflacion(diccionario_datos, producto, fechas)
        inflacion_total_producto = 0
        for supermecado, inflacion_parcial_producto in inflacion:
            inflacion_total_producto += inflacion_parcial_producto
        inflacion_promedio += inflacion_total_producto / len(inflacion)
    return (inflacion_promedio / len(diccionario_datos.keys())), fechas


# ----------------------------------------------------------------------
# |                         Mejor Precio Producto                      |
# ----------------------------------------------------------------------

def mejor_precio_supermercado(diccionario_datos, producto, fecha):
    """Recibe como parametro un diccionario, el nombre de un producto y una fecha.
    Devuelve el precio más bajo  y el nombre del supermecado que vende el producto a ese precio"""
    supermecado = diccionario_datos.get(producto, {})
    supermercado_mejor_precio = ''
    mejor_precio = None
    for clave in supermecado:
        try:
            dicc_fechas = supermecado[clave]
            precio = dicc_fechas.get(fecha, None)
            if not mejor_precio:  # el primer precio siempre va a ser el mejor precio
                mejor_precio = precio
                supermercado_mejor_precio = clave
            elif precio < mejor_precio:
                mejor_precio = precio
                supermercado_mejor_precio = clave
        except TypeError:
            # si el supermercado no vende el producto en esa fecha, pasa al siguiente
            continue
    return supermercado_mejor_precio, mejor_precio


# -----------------------------------------------------------------------
# |                 Interfaz e impresión en pantalla                    |
# -----------------------------------------------------------------------


def mostrar_inflacion_promedio(inflacion_promedio):
    """Recibe una tupla con la inflacion promedio y una tupla de fechas
    y los imprime por pantalla"""
    print("La inflacion general promedio entre las fechas {} y {} es : {:.2f}% ".format(
        inflacion_promedio[1][0], inflacion_promedio[1][1], inflacion_promedio[0]))


def mostrar_inflacion(lista):
    """Recibe como parametro una secuencia.
    Imprime por pantalla los diferentes supermercados y su inflacion"""
    try:
        for supermercado, inflacion in lista:
            print("La inflacion del supermercado {} para ese producto es {:.2f}% ".format(
                supermercado, inflacion))
    except:
        raise TypeError(
            "El producto no se vende en ninguno de los supermercados para ese rango de fechas")


def mostrar_mejor_precio(supermercado, precio):
    try:
        print(
            "El precio más bajo del producto es ${:.2f} y se encuentra en el supermercado {}".format(
                precio, supermercado))
    except TypeError:  # Si el producto no se vende en ningun supermercado
        #  para esa fecha, tira error
        raise TypeError("El producto no se vende en ninguno de los supermercados para esa fecha ")


def mostrar_menu():
    """Imprime el menú principal"""
    print('------\nMenú principal \n------')
    imprimir_opciones(LISTA_OPCIONES)
    print('------')


def imprimir_fallidos(lista):
    """Imprime una lista de los registros ignorados por tener mas o menos campos
    que los esperados"""
    if lista:
        listaaux = []
        for registro in lista:
            listaaux += [",".join(campo for campo in registro)]
        print('Los siguientes registros se han ignorado por inconsistencia de datos:')
        imprimir_opciones(listaaux)


def imprimir_opciones(lista):
    """Imprime una lista de opciones"""
    for x in range(len(lista)):
        print(str(x + 1) + ". " + str(lista[x]))


# -----------------------------------------------------------------------------
# |                             Ingreso datos                                 |
# -----------------------------------------------------------------------------


def pedir_opcion(cantidad=CANT_OPCIONES):
    """Pide el ingreso de una opcion"""
    return verif_ingreso_opcion(input("Su elección: "), cantidad)


def pedir_fecha():
    """Pide el ingreso de una fecha (año,mes) y se devuelve como
    una cadena de la forma 'AAAAMM'"""
    print("Ingrese una fecha")
    año = verif_ingreso_año(input("Año (en formato AAAA): "))
    mes = verif_ingreso_mes(input("Mes (número): "))
    return año + mes


def pedir_producto(diccionario_datos):
    """Pide un nombre de producto (o una parte de él)"""
    while True:
        try:
            ingresado = verif_ingreso_producto(input('Producto buscado: '), diccionario_datos)
            return ingresado
        except ValueError:
            print('Debes ingresar por lo menos una letra.')


# ----------------------------------------------------------------------------
# |                             Verificaciones                               |
# ----------------------------------------------------------------------------
def buscar_producto_ingresado(cadena, diccionario_datos):
    """Busca la cadena en el diccionario pasado por parámetro y devuelve
    todas las claves que contienen la cadena en forma de lista, desordenada"""
    listaaux = []
    for nombre_producto in diccionario_datos:
        if cadena.lower() in nombre_producto.lower():
            listaaux += [nombre_producto]

    return listaaux


def verif_ingreso_producto(cadena, diccionario_datos):
    """Dada una cadena 'de busqueda' y un diccionario, muestra todos los productos
    que contengan la cadena y se solicita que se elija uno de ellos. Devuelve
    la descripcion del producto elegido"""
    if cadena == '':
        raise ValueError
    encontrados = buscar_producto_ingresado(cadena, diccionario_datos)
    imprimir_opciones(encontrados)
    buscado = encontrados[pedir_opcion(len(encontrados)) - 1]
    return buscado


def verif_ingreso_mes(cadena):
    """Solicita se ingrese una cadena hasta que sea un mes y se devuelve"""
    while not es_mes(cadena):
        cadena = input('Ingrese el número de mes: ')
    if len(cadena) == 1:
        return '0' + cadena
    return cadena


def verif_ingreso_año(cadena):
    """Solicita se ingrese una cadena hasta que sea un año y se devuelve"""
    while not es_año(cadena):
        cadena = input('Ingrese el año en formato AAAA: ')
    return cadena


def verif_ingreso_opcion(cadena, cantidad):
    """Recibe una cadena ingresada por el usuario y no la devuelve hasta que
    sea un número perteneciente a las opciones posibles"""
    while not es_numero_opcion(cadena, cantidad):
        cadena = input("Ingrese un número de opción: ")
    return int(cadena)


def es_numero_opcion(cadena, cantidad_opciones):
    """Verifica que la cadena sea una de las opciones posibles, establecidas por la
    cantidad pasada por parámetro"""
    return cadena.isdigit() and int(cadena) <= cantidad_opciones


def es_mes(cadena):
    """Verifica que la cadena sea un mes (en números)"""
    return cadena.isdigit() and 12 >= int(cadena) > 0


def es_año(cadena):
    """Verifica que la cadena sea un año"""
    return cadena.isdigit() and len(cadena) == 4 and 0 < int(cadena) <= AÑO


main()
