# -*- coding: utf-8 -*-
import logging
from odoo import models

_logger = logging.getLogger(__name__)

# Límite de caracteres para descripción según SIN Bolivia
MAX_DESCRIPTION_LENGTH = 150


class AccountMove(models.Model):
    """Extensión de account.move para truncar descripciones"""
    _inherit = "account.move"

    def _get_detail_move_line(self, type_sector: int = 1):
        """
        Extiende el método original para truncar descripciones a 150 caracteres.
        
        El webservice de facturación SIN de Bolivia tiene un límite de 150 
        caracteres para el campo descripción. Este método asegura que ninguna
        descripción exceda ese límite.
        
        Args:
            type_sector (int): Tipo de sector del documento (1: Factura, 24: Nota)
            
        Returns:
            list: Lista de diccionarios con detalles de líneas de factura
        """
        # Llamar al método original del padre
        detail = super(AccountMove, self)._get_detail_move_line(type_sector)
        
        # Truncar descripciones que excedan el límite
        for item in detail:
            if 'description' in item and item['description']:
                original_length = len(item['description'])
                
                # Truncar si excede el límite
                if original_length > MAX_DESCRIPTION_LENGTH:
                    item['description'] = item['description'][:MAX_DESCRIPTION_LENGTH]
                    
                    # Log para seguimiento (opcional, puede comentarse en producción)
                    _logger.info(
                        f"Descripción truncada de {original_length} a {MAX_DESCRIPTION_LENGTH} caracteres. "
                        f"Original: '{item['description'][:50]}...'"
                    )
        
        return detail
