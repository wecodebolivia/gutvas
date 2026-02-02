# -*- coding: utf-8 -*-
import logging
from odoo import models

_logger = logging.getLogger(__name__)

# Límite de caracteres para descripción según SIN Bolivia
MAX_DESCRIPTION_LENGTH = 150


class AccountMove(models.Model):
    """Extensión de account.move para modificar descripción del web service"""
    _inherit = "account.move"

    def _get_detail_move_line(self, type_sector: int = 1):
        """
        Extiende el método original para:
        1. Cambiar descripción a solo nombre del producto con variantes (sin código)
        2. Truncar descripciones a 150 caracteres si exceden el límite
        
        El webservice de facturación SIN de Bolivia:
        - Tiene un límite de 150 caracteres para el campo descripción
        - Requiere información clara del producto
        
        Args:
            type_sector (int): Tipo de sector del documento (1: Factura, 24: Nota)
            
        Returns:
            list: Lista de diccionarios con detalles de líneas de factura
        """
        # Llamar al método original del padre
        detail = super(AccountMove, self)._get_detail_move_line(type_sector)
        
        # Procesar cada línea para modificar la descripción
        for item in detail:
            if 'description' in item:
                # Buscar la línea de factura correspondiente por código de producto
                product_code = item.get('codeProduct', '')
                
                if product_code:
                    # Buscar la línea de factura que coincida con el código
                    invoice_line = self.invoice_line_ids.filtered(
                        lambda l: l.product_id and l.product_id.default_code == product_code
                    )[:1]
                    
                    if invoice_line and invoice_line.product_id:
                        product = invoice_line.product_id
                        product_template = product.product_tmpl_id
                        
                        # Construir nombre del producto con variantes
                        product_name = product_template.name
                        
                        # Agregar atributos de variante si existen
                        if product.product_template_variant_value_ids:
                            variant_names = product.product_template_variant_value_ids.mapped('name')
                            if variant_names:
                                variant_str = ', '.join(variant_names)
                                product_name = f"{product_name} ({variant_str})"
                        
                        # Verificar si hay nota del cliente (del método original)
                        # La descripción original puede tener formato "nombre (nota)"
                        original_desc = item['description']
                        note = None
                        
                        # Extraer nota si existe en la descripción original
                        if '(' in original_desc and original_desc.endswith(')'):
                            parts = original_desc.rsplit('(', 1)
                            if len(parts) == 2:
                                potential_note = parts[1].rstrip(')')
                                # Solo considerar como nota si no es parte de variantes
                                if potential_note and potential_note not in product_name:
                                    note = potential_note
                        
                        # Construir descripción final
                        if note:
                            item['description'] = f"{product_name} ({note})"
                        else:
                            item['description'] = product_name
                        
                        _logger.debug(
                            f"Descripción modificada para {product_code}: '{item['description']}'"
                        )
                
                # Truncar si excede el límite de 150 caracteres
                if item['description']:
                    original_length = len(item['description'])
                    
                    if original_length > MAX_DESCRIPTION_LENGTH:
                        item['description'] = item['description'][:MAX_DESCRIPTION_LENGTH]
                        
                        _logger.info(
                            f"Descripción truncada de {original_length} a {MAX_DESCRIPTION_LENGTH} caracteres. "
                            f"Producto: {product_code}"
                        )
        
        return detail
