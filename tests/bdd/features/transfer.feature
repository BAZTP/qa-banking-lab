Feature: Transferencias educativas
  Scenario: Transferencia válida entre cuentas ficticias
    Given Ana inició sesión con sus cuentas de práctica
    When transfiere 10.25 entre sus cuentas
    Then su cuenta de origen tiene 989.75 y existe una operación

  Scenario: Rechazo por saldo insuficiente
    Given Ana inició sesión con sus cuentas de práctica
    When intenta transferir 1000.01
    Then se rechaza sin cambiar el saldo ni el historial
