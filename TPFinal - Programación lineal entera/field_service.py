import sys
import cplex

TOLERANCE =10e-6

class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])
        

class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        

    def load(self,filename):
        # Abrimos el archivo.
        f = open(filename)

        # Leemos la cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Leemos la cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Leemos cada una de las ordenes.
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            row = f.readline().split(' ')
            orden = Orden()
            orden.load(row)
            self.ordenes.append(orden)
        
        # Leemos la cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Leemos los conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            row = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Leemos las ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            row = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Leemos las ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            row = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,row)))
        
        
        # Leemos la cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Leemos las ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            row = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,row)))
        
        # Cerramos el archivo.
        f.close()


def get_instance_data():
    file_location = sys.argv[1].strip()
    instance = FieldWorkAssignment()
    instance.load(file_location)
    return instance
    

def populate_by_row(my_problem, data):
    
    # W_i_r es una binaria que vale 1 si el trabajador i completó las 5 órdenes del rango r y continúa al próximo rango.
    W = {}  # Diccionario para almacenar las variables Wir
    for i in range(data.cantidad_trabajadores):
        for r in range(3):  # 3 rangos por completar y habilitar a un siguiente.
            var_name = f'W_{i}_{r}'  # Nombre de la variable en formato W_i_r
            my_problem.variables.add(obj=[0], lb=[0], ub=[1], types=['B'], names=[var_name])
            W[(i, r)] = var_name

    # Y_i_r captura la cantidad de órdenes que cada trabajador i completó en cada rango r.
    # Cada rango incluye un máximo de 5 órdenes (el máximo a trabajar son 5 días x 4 turnos = 20 órdenes semanales).
    # Esta variable interviene en la función objetivo, capturando el costo vía coeficientes negativos.
    Y = {}  # Diccionario para almacenar las variables Yir
    costos_por_orden = [-1000,-1200,-1400,-1500] # Valores definidos en el enunciado.
    for i in range(data.cantidad_trabajadores):
        for r in range(4):  # 4 rangos posibles.
            var_name = f'Y_{i}_{r}'
            coeficiente = costos_por_orden[r]
            my_problem.variables.add(obj=[coeficiente], lb=[0], ub=[5], types=['I'], names=[var_name])
            Y[(i, r)] = var_name

    # D_i_d es una binaria que vale 1 si el trabajador i realizó alguna orden el día d
    D = {}  # Diccionario para almacenar las variables Did
    for i in range(data.cantidad_trabajadores):
        for d in range(6):  # 6 días laborales
            var_name = f'D_{i}_{d}'
            my_problem.variables.add(obj=[0], lb=[0], ub=[1], types=['B'], names=[var_name])
            D[(i, d)] = var_name 

    # Z_o_t_d es una binaria que vale 1 cuando se realiza la orden o en el turno t del día d.
    Z = {} # Diccionario para almacenar las variables Zotd.
    for o in range(data.cantidad_ordenes):
        for t in range(5):  # 5 turnos por día.
            for d in range(6):  # 6 días laborables.
                var_name = f'Z_{o}_{t}_{d}'
                coeficiente_objetivo = (data.ordenes[o].beneficio / data.ordenes[o].trabajadores_necesarios)
                my_problem.variables.add(obj=[0], lb=[0], ub=[1], types=['B'], names=[var_name])
                Z[(o, t, d)] = var_name

    # X_i_t_o_d es una binaria que vale 1 cuando el trabajador i realiza la orden o en el turno t del día d.
    # Esta variable interviene en la función objetivo, capturando el beneficio vía coeficientes positivos.
    X = {}  # Diccionario para almacenar las variables Xitod  
    for i in range(data.cantidad_trabajadores):
        for t in range(5):  # 5 turnos por día
            for o in range(data.cantidad_ordenes):
                for d in range(6):  # 6 días en la planificación
                    var_name = f'X_{i}_{t}_{o}_{d}'
                    coeficiente_objetivo = (data.ordenes[o].beneficio / data.ordenes[o].trabajadores_necesarios)
                    my_problem.variables.add(obj=[coeficiente_objetivo], lb=[0], ub=[1], types=['B'], names=[var_name])
                    X[(i, t, o, d)] = var_name

    # Seteamos direccion del problema
    # Buscamos maximizar el beneficio neto (beneficio - costo).
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.minimize)
    
    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion.
    add_constraint_matrix(my_problem, data, D, X, W, Y, Z)
    
    # Exportamos el LP cargado en myprob con formato .lp.
    # Util para debug.
    my_problem.write('balanced_assignment.lp')

def add_constraint_matrix(my_problem, data, D, X, W, Y, Z):
    
    ### Restricciones de la función lineal a trozos. ###
    # Ya habíamos definido que la variable Y podía tomar valores entre cero y cinco.
    # Para el rango cero, volvemos a reflejar ese límite.
    # Restricción Y_i_0 <= 5
    for i in range(data.cantidad_trabajadores):
        indices = [Y[(i,0)]]
        values = [1]
        row = [indices, values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[5])

    # Si la W correspondiente al primer rango (Wi0) se activa, debemos tener completo ese rango salarial (Yi0).
    # Restricción Y_i_0 >= W_i_0 * 5 ---> Y_i_0 - 5 * W_i_0 >= 0
    for i in range(data.cantidad_trabajadores):
        indices_min = [Y[(i,0)]]
        indices_max = [W[(i,0)]]
        values_min = [1]
        values_max = [-5]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])

    # Únicamente podemos acceder al Y de segundo rango si se activó el W que nos indica que el rango precedente se completó (W0).
    # Restricción Y_i_1 <= W_i_0 * 5
    for i in range(data.cantidad_trabajadores):
        indices_min = [Y[(i,1)]]
        indices_max = [W[(i,0)]]
        values_min = [1]
        values_max = [-5]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # Si la W correspondiente al segundo rango (Wi1) se activa, debemos tener completo ese rango salarial (Yi1).
    # Restricción Y_i_1 >= W_i_1 * 5
    for i in range(data.cantidad_trabajadores):
        indices_min = [Y[(i,1)]]
        indices_max = [W[(i,1)]]
        values_min = [1]
        values_max = [-5]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])

    # Únicamente podemos acceder al Y de tercer rango (Y2) si se activó el W que nos indica que el rango precedente se completó (W1).
    # Restricción Y_i_2 <= W_i_1 * 5
    for i in range(data.cantidad_trabajadores):
        indices_min = [Y[(i,2)]]
        indices_max = [W[(i,1)]]
        values_min = [1]
        values_max = [-5]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])


    # Si la W correspondiente al tercer rango (Wi2) se activa, debemos tener completo ese rango salarial (Yi2).
    # Restricción Y_i_2 >= W_i_2 * 5
    for i in range(data.cantidad_trabajadores):
        indices_min = [Y[(i,2)]]
        indices_max = [W[(i,2)]]
        values_min = [1]
        values_max = [-5]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])

    # Accedemos al Y de cuarto rango (Y3) si se activó el W que nos indica que el rango precedente se completó (W2).
    # Restricción Y_i_3 <= W_i_2 * 5
    for i in range(data.cantidad_trabajadores):
        indices_min = [Y[(i,3)]]
        indices_max = [W[(i,2)]]
        values_min = [1]
        values_max = [-5]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # # No es necesaria esta restricción ya que en el último nivel, no controlamos nivel de saturación de ese nivel.
    # # Restricción Y_i_3 >= W_i_3 * 5 
    # for i in range(data.cantidad_trabajadores):
    #     indices_min = [Y[(i,3)]]
    #     indices_max = [W[(i,3)]]
    #     values_min = [1]
    #     values_max = [-5]
    #     row = [indices_min + indices_max, values_min + values_max]
    #     my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])


    ### Si se prende un rango salarial si o si se requiere que se haya prendido el anterior. ###
    # Esto nos permite no saltear rangos y completarlos en forma ordenada.
    # Si indicamos prendido el rango 1 es porque antes habíamos indicado prendido el rango cero.
    # Restricción W_i_0 >= W_i_1 ----> W_i_0 - W_i_1 >= 0
    for i in range(data.cantidad_trabajadores):
        indices_min = [W[(i,0)]]
        indices_max = [W[(i,1)]]
        values_min = [1]
        values_max = [-1]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])

    # Si indicamos prendido el rango 2 es porque antes habíamos indicado prendido el rango 1.
    # Restricción W_i_1 - W_i_2 >= 0
        indices_min = [W[(i,1)]]
        indices_max = [W[(i,2)]]
        values_min = [1]
        values_max = [-1]
        row = [indices_min + indices_max, values_min + values_max]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])

    # # Restricción W_i_2 - W_i_3 >= 0
    #     indices_min = [W[(i,2)]]
    #     indices_max = [W[(i,3)]]
    #     values_min = [1]
    #     values_max = [-1]
    #     row = [indices_min + indices_max, values_min + values_max]
    #     my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])


    ### Vinculamos variable X y variable Y. ###
    # La suma de las órdenes realizadas por cada trabajador en la semana (X)
    # debe ser igual a la suma de las órdenes en los distintos rangos salariales (Y).
    for i in range(data.cantidad_trabajadores):
        indices_sem = [X[(i,t,o,d)] for t in range(5) for d in range(6) for o in range(data.cantidad_ordenes)]
        values_sem = [1] * (5 * 6 * data.cantidad_ordenes)
        indices_rango = [Y[(i, r)] for r in range (4)]
        values_rango = [-1] * 4        
        row = [indices_sem + indices_rango, values_sem + values_rango]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['E'], rhs=[0])



    # Cada trabajador solo puede realizar una orden en cada turno de cada día.
    for i in range(data.cantidad_trabajadores):
        for t in range(5):
            for d in range(6):
                indices = [X[(i, t, o, d)] for o in range(data.cantidad_ordenes)]
                values = [1] * data.cantidad_ordenes
                row = [indices, values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])



    ### Pra restringir la cantidad de días trabajados en la semana debemos vincular la variable X y la D. ###
    # La suma de órdenes realizadas en los distintos turnos (X) menos la cantidad de días trabajados (D) debe ser mayor o igual a cero.
    # La variable D vale 1 cuando el trabajador realiza alguna orden.
    # Sin embargo, esta restricción permite que habiendo realizado alguna orden, la variable D valiera cero.
    # Restricción: X - D >= 0 (permite X=1 y D=0).
    for i in range(data.cantidad_trabajadores):
        for d in range(6):
            indices_sem = [X[(i, t, o, d)] for t in range(5) for o in range(data.cantidad_ordenes)]
            values_sem = [1] * (5*data.cantidad_ordenes)
            indices_dia = [D[(i, d)]]
            values_dia = [-1]
            row = [indices_sem + indices_dia, values_sem + values_dia]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[0])
    
    # Complementamos con la suma de órdenes realizadas en los distintos turnos (X) menos cuatro veces el valor de la variable D debe ser menor o igual a cero.
    # Aunque permite que no se realicen órdenes pero D esté activado, entre ambas restricciones se cubren la totalidad de los escenarios.
    # Restricción: X-4D <= 0 (permite X=0 y D=1)
            values_dia = [-4] # Máximo de órdenes a realizar por día (no puede trabajar los 5 turnos del día)
            row = [indices_sem + indices_dia, values_sem + values_dia]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # Restricción: Ningún trabajador puede trabajar los 6 días de la planificación.
    for i in range(data.cantidad_trabajadores):
        indices = [D[(i,d)] for d in range(6)]
        values = [1] * 6  # 6 días laborables
        row = [indices, values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[5])  # Limitado a 5 días



    # Restricción: Ningún trabajador puede trabajar los 5 turnos de un día.
    for i in range(data.cantidad_trabajadores):
        for d in range(6):
            indices = [X[(i, t, o, d)] for t in range(5) for o in range(data.cantidad_ordenes)]
            values = [1] * (5 * data.cantidad_ordenes)
            row = [indices, values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[4])  # Limitado a 4 turnos



    # Restricción: Órdenes Confictivas (A-B), no pueden asignarse en turnos consecutivos de un mismo trabajador.
    # Consideramos hacer primero la orden A y luego la B.
    for (oa, ob) in data.ordenes_conflictivas:
        for i in range(data.cantidad_trabajadores):
            for d in range(6):
                for t in range(4):  # Solo 4 turnos para tener uno más consecutivo.
                    indices = [X[(i, t, oa, d)], X[(i, t + 1, ob, d)]]
                    values = [1, 1]
                    row = [indices, values]
                    my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])
    
    # Pero también realizar primero la orden B y luego la A.
                    indices = [X[(i, t, ob, d)], X[(i, t + 1, oa, d)]]
                    values = [1, 1]
                    row = [indices, values]
                    my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])



    # Restricción: Si una orden se realiza, debe tener asignados sus trabajadores necesarios en el mismo turno el mismo día.
    # Comparamos la variable Z que indica si se realizó la orden versus la cantidad de trabajadores que intervienen en realizarla ponderador por la inversa de To.
    for o in range(data.cantidad_ordenes):
        for t in range(5):
            for d in range(6):
                indices_x = [X[(i, t, o, d)] for i in range(data.cantidad_trabajadores)]
                values_x = [1 / data.ordenes[o].trabajadores_necesarios] * data.cantidad_trabajadores
                indices_z = [Z[(o, t, d)]]
                values_z = [-1]
                row = [indices_z + indices_x, values_z + values_x]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['E'], rhs=[0])



    # Restricción: Órdenes correlativas (A-B) deben asignarse en turnos consecutivos del mismo día y realizarse por cualquier empleado.
    # Si la orden A se realiza, al tener coeficientes positivos, nos obliga a hacer la orden B para poder cumplir con la desigualdad planteada (menor o igual a cero).
    # Los coeficientes de la orden B son negativos para permitirnos realizar la orden B sin necesidad de realizar la orden A. 
    for (oa, ob) in data.ordenes_correlativas:
        for d in range(6):
            for t in range(4):  # Solo 4 turnos para tener uno más consecutivo.         
                indices = []
                values = []
                for i in range(data.cantidad_trabajadores):
                    indices.extend([X[(i, t, oa, d)], 
                                    X[(i, t + 1, ob, d)]])
                    values.extend([1 / data.ordenes[oa].trabajadores_necesarios, 
                                   -1 / data.ordenes[ob].trabajadores_necesarios])       
                row = [indices, values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])



    # Restricción: Diferencia entre trabajadores no mayor a 10 órdenes.
    # Comparamos la cantidad de órdenes de todos los trabajadores entre sí.
    total_por_trabajador = {}
    for i in range(data.cantidad_trabajadores):
        total_por_trabajador[i] = [X[(i, t, o, d)] for t in range(5) for d in range(6) for o in range(data.cantidad_ordenes)]

    for i in range(data.cantidad_trabajadores):
        for j in range(data.cantidad_trabajadores):
            if j != i:
                indices_i = [total_por_trabajador[i][t * 6 * data.cantidad_ordenes + d * data.cantidad_ordenes + o] for t in range(5) for d in range(6) for o in range(data.cantidad_ordenes)]
                indices_j = [total_por_trabajador[j][t * 6 * data.cantidad_ordenes + d * data.cantidad_ordenes + o] for t in range(5) for d in range(6) for o in range(data.cantidad_ordenes)]
                values_i = [1] * (5 * 6 * data.cantidad_ordenes)
                values_j = [-1] * (5 * 6 * data.cantidad_ordenes)
                row = [indices_i + indices_j, values_i + values_j]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[10])



def solve_lp(my_problem, data):
    # Resolvemos el ILP.
    
    # Aceptamos un gap entre cotas de un 0.1%
    my_problem.parameters.mip.tolerances.mipgap.set(0.001)
    
    my_problem.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ', objective_value)
    print('Status solucion: ', status_string,'(' + str(status) + ')')
    # print(len(x_variables))
    # print(x_variables)

    # Imprimimos las variables usadas en el orden en que fueron definidas.
    # Variable W
    for i in range(data.cantidad_trabajadores):
        for r in range(3):
            var_w_index = i * 3 + r
            value_w = x_variables[var_w_index]
            # print(var_w_index)
            # Tomamos esto como valor de tolerancia, por cuestiones numericas.
            if value_w > TOLERANCE:
                print(f'W_{i}_{r}: {value_w}')
    print("")

    # Variable Y
    for i in range(data.cantidad_trabajadores):
        for r in range(4):
            var_y_index = i * 4 + r
            value_y = x_variables[var_y_index + (data.cantidad_trabajadores * 3)]
            # print(var_y_index + (data.cantidad_trabajadores * 4))
            # Tomamos esto como valor de tolerancia, por cuestiones numericas.
            if value_y > TOLERANCE:
               print(f'Y_{i}_{r}: {value_y}')
    print("")

    # Variable D
    for i in range(data.cantidad_trabajadores):
        for d in range(6):
            var_d_index = i * 6 + d
            value_d = x_variables[var_d_index + (data.cantidad_trabajadores * 3) + (data.cantidad_trabajadores * 4)]
            # print(var_d_index + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 4))
            # Tomamos esto como valor de tolerancia, por cuestiones numericas.
            if value_d > TOLERANCE:
               print(f'D_{i}_{d}: {value_d}')
    print("")

    # Variable Z
    for o in range(data.cantidad_ordenes):
        for t in range(5):
            for d in range(6):
                var_z_index =  o * (5*6) + t * 6 + d
                value_z = x_variables[var_z_index + (data.cantidad_trabajadores * 3) + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 6)]
                # print(var_z_index + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 6))
                # Tomamos esto como valor de tolerancia, por cuestiones numericas.
                if value_z > TOLERANCE:
                    print(f'Z_{o}_{t}_{d}: {value_z}')
    print("")

    # Variable X
    for i in range(data.cantidad_trabajadores):
        for t in range(5):
            for o in range(data.cantidad_ordenes):
                for d in range(6):
                    var_x_index = i * (5 * data.cantidad_ordenes * 6) + t * (data.cantidad_ordenes * 6) + o * (6) + d
                    value_x = x_variables[var_x_index + (data.cantidad_trabajadores * 3) + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 6) + (data.cantidad_ordenes * (5 * 6))]
                    # print (var_x_index + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 4) + (data.cantidad_trabajadores * 6) + (data.cantidad_ordenes * (5 * 6)))
                    # Tomamos esto como valor de tolerancia, por cuestiones numericas.
                    if value_x > TOLERANCE:
                        print(f'X_{i}_{t}_{o}_{d}: {value_x}')


def main():
    
    # Obtenemos los datos de la instancia.
    data = get_instance_data()
    
    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)

if __name__ == '__main__':
    main()
