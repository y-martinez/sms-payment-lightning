HELP_MESSAGE = (
    "Acciones disponibles:\n\n"
    "CREAR: crear tu cuenta\n"
    "RECARGAR: recargar BTC a tu cuenta\n"
    "SALDO: consultar tu saldo\n"
    "ENVIAR : transferir dinero a un usuario\n"
    "PAGAR: pagar una factura"
)

USER_CREATED = (
    "Su cuenta se ha creado exitosamente, para agregar fondos envie un sms con "
    "la operacion RECARGAR"
)

USER_RELOAD_FUNDS = {
    "start": (
        "Envie BTC a su direccion %s para agregar fondos, "
        "recuerde que SMS Payment se encuentra en version beta, no envie "
        "mas de $50 o su equivalente en BTC"
    ),
    "end": (
        "Hemos registrado el %s, %s BTC ($%s) en su cuenta y tu balance "
        "actual es de %s BTC ($%s)"
    ),
}

USER_BALANCE = (
    "El balance actual en su cuenta es de %s BTC ($%s) a una tasa de $%s por BTC el %s"
)

USER_PAYMENT = {
    "successful_payer": "Pagados %s BTC ($%s) al %s exitosamente",
    "successful_payee": "Recibido un pago de %s BTC ($%s)",
    "insufficient_funds": "Fondos insuficientes, pago rechazado",
    "user_invalid": "Destinatario no registrado en el sistema, pago no realizado",
    "failed": "Error al realizar el pago intente de nuevo mas tarde",
}

USER_PAYMENT_INVOICE = {
    "successful": "Factura pagada exitosamente, con una comision de %s BTC",
    "insufficient_funds": "Fondos insuficientes, pago rechazado",
    "failed": "Error al realizar el pago intente de nuevo mas tarde",
}

ERROR_MESSAGES = {
    "operation_error": (
        "Error en la operacion, si tiene dudas con las acciones"
        " disponibles escriba AYUDA para obtener informacion"
    )
}
