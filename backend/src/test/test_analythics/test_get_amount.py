from src.analytics_reports.repository.get_analytics import GetAnalytics

"""
def test_pagos_por_mes() -> None:
    get_analytics = GetAnalytics()
    datos =  get_analytics.get_amount_for_year('M010', 'agua', 'Y24')

    for dato in datos:
        print(dato)
    assert isinstance(datos, list)




"""

def test_pagtest_ganacias_por_mes() -> None:
    get_analytics = GetAnalytics()
    datos =  get_analytics.get_bills_by_month('M010', 'agua', 'Y24')

    for dato in datos:
        print(dato)
    assert isinstance(datos, list)