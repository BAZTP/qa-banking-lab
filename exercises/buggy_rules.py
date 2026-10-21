"""Funciones defectuosas AISLADAS: app/ no importa este módulo.

No hay flag para activarlas en la API. Solo se ejecutan al practicar tests aquí.
"""


def accepts_amount(amount):
    # BUG-01: acepta cero, contrario al criterio CA-03.
    return amount >= 0


def can_transfer(balance, amount):
    # BUG-02: rechaza gastar exactamente el saldo disponible.
    return balance > amount
