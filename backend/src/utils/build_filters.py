from src.dim_dates.dim_date import DIM_DATE

class BuildFilters:
    """
    Clase clase proporciona metodos comunes para poder contruir filtros mediante, recurosso que son utilizados por multiples clases como lo pdorian ser los
    filtros de manzana y algunos para obtnenr la fecha 
    """
    def build_manzana_condition(self, manzanas: list) -> tuple[str, list]:
        """
        Construye la condición SQL para filtrar por manzanas.
        
        Args:
            manzanas (list): Lista de nombres de manzanas a filtrar
            
        Returns:
            tuple: (condicion_sql, valores) donde:
                - condicion_sql: string con la condición OR
                - valores: lista de valores para los parámetros
        """
        condiciones = []
        valores = []
        
        manzanas_mapping = {
            "cerritos": "p.CustomerFraction = ?",
            "centro": "p.CustomerFraction = ?",
            "yhonda": "p.CustomerFraction = ?",
            "tepetate": "p.CustomerFraction = ?",
            "garambullo": "p.CustomerFraction = ?",
            "buenavista": "p.CustomerFraction = ?",
        }
        
        for manzana in manzanas:
            manzana_norm = str(manzana).strip().lower()
            if manzana_norm in manzanas_mapping:
                condiciones.append(manzanas_mapping[manzana_norm])
                valores.append(manzana_norm)

        return " OR ".join(condiciones), valores
    

    def add_date(self, fechafiscal: str) -> tuple[str, list]:
        """
        Genera condiciones SQL para filtros de fecha fiscal
        
        Args:
            fechafiscal (str): Tipo de fecha fiscal ('FiscalYear', 'FiscalMonth', etc.)
            
        Returns:
            tuple: (condicion_sql, valores) donde:
                - condicion_sql: string con la condición WHERE (ej: "d.FiscalYear = ?")
                - valores: lista de valores para los parámetros
        """
        if not fechafiscal:
            return "", []
        
        try:
            dim_date = DIM_DATE()
            fechas = dim_date.generar_fechas(fechafiscal)
            
            if not fechas:
                return "", []
            
            condiciones = []
            valores = []
            
            for clave, valor in fechas.items():
                condiciones.append(f"d.{clave} = ?")
                valores.append(valor)
            
            condicion_sql = " AND ".join(condiciones)
            print(f"[DEBUG] Generadas condiciones de fecha: {condicion_sql}")
            
            return condicion_sql, valores
            
        except Exception as e:
            print(f"[ERROR] Error al procesar fechas fiscales: {str(e)}")
            return "", []
    

