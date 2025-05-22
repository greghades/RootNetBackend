from .randCodes import generatedCode


def get_email_content(code):
    """
    Generates the HTML content for the email based on the provided code.
    """

    PASSWORD_RESET = f"""
    <html>
        <body style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>
            <h2 style='color: #2c3e50;'>Código de Verificación</h2>
            <p>Estimado/a usuario/a,</p>
            <p>Para continuar con el proceso de verificación, utilice el siguiente código:</p>
            <h3 style='background-color: #f4f4f4; padding: 10px; display: inline-block;'>{code.changePasswordCode}</h3>
            <p>Este código es válido por un tiempo limitado. Por favor, ingréselo en el formulario correspondiente.</p>
            <p>Si no solicitó este código, puede ignorar este correo.</p>
            <p>Gracias,<br>El equipo de RootNet</p>
        </body>
    </html>
    """
    
    return PASSWORD_RESET.format(code=code)
