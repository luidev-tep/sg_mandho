class SpecialServices:
    

    def is_already_paid(self, year_registers: list[tuple])-> list[tuple]:
        """
        Filtra los registros de pagos anuales de un servicio especial como el agua.

        Este método se utiliza para servicios que solo necesitan ser pagados una vez al año.
        Identifica los años en los que el cliente ha pagado por completo el servicio
        y devuelve una lista de los registros correspondientes a esos años.
        
        La lógica se basa en que, para servicios de agua, un pago completo está
        compuesto por dos registros ('tomas' y 'consumo'). Si ambos existen para un
        año, el servicio se considera pagado para ese año.

        Args:
            year_registers (list[tuple]): Una lista de tuplas donde cada tupla
                                          contiene la información de un servicio.
                                          Ejemplo: [('Y20', 'consumo', 360.0), ('Y20', 'tomas', 360.0)]

        Returns:
            list[tuple]: Una lista de tuplas que representan los registros de
                         los años que ya han sido pagados en su totalidad.
        """
        # Se convierten a una lista de años para contarlos.
        years = [year[0] for year in year_registers]

        # Se crea un diccionario para contar la frecuencia de cada año.
        count_years = {year: 0 for year in set(years)}

        # Se itera sobre los registros para contar cuántos servicios hay por año.
        for year in year_registers:
            count_years[year[0]] += 1
            
        # Se obtienen los años que se consideran pagados.
        # En el caso del agua, un año se considera pagado si tiene 2 registros.
        years_paid = [year for year in count_years.keys() if count_years[year] == 2]
        
        # Se filtran los registros originales para devolver solo los que pertenecen a años pagados.
        return [year_register for year_register in year_registers if year_register[0] in years_paid]