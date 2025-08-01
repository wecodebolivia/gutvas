from odoo import models, fields


class CucuCatalogsProductService(models.Model):
    _name = "cucu.catalogs.product.service"
    _rec_name = "description"
    _description = "Cucu product service"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    code_product = fields.Char("Code product")
    is_visible = fields.Boolean("Visible", default=True)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, product_service):
        company_id = self.env.companies.id
        db_product = self.env["cucu.catalogs.product.service"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_product) > 0:
            map_ids = list(map(lambda product_id: product_id["code_type"], db_product))
            for rec in product_service:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in product_service:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "code_product": data["codeProduct"],
                "company_id": self.env.companies.id,
            }
        )

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code_product} - {record.description}"

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.product.service"].search(
            [("id", "in", self.ids)]
        )
        for rec in select:
            self.write({"is_visible": True})


class CucuCatalogsActivities(models.Model):
    _name = "cucu.catalogs.activities"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    code_type_activity = fields.Char("Code Type Activity")
    is_visible = fields.Boolean("Visible", default=True)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, activities):
        company_id = self.env.companies.id
        db_activities = self.env["cucu.catalogs.activities"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_activities) > 0:
            map_ids = list(map(lambda doc_db: doc_db["code_type"], db_activities))
            for rec in activities:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in activities:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "code_type_activity": data["codeTypeActivity"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.activities"].search([("id", "in", self.ids)])
        for rec in select:
            self.write({"is_visible": True})

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code_type} - {record.description}"


class CucuCatalogsEventSignificant(models.Model):
    _name = "cucu.catalogs.event.significant"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    is_visible = fields.Boolean("Visible", default=True)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, event_significant):
        company_id = self.env.companies.id
        db_significant = self.env["cucu.catalogs.event.significant"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_significant) > 0:
            map_ids = list(map(lambda doc_db: doc_db["code_type"], db_significant))
            for rec in event_significant:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in event_significant:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.event.significant"].search(
            [("id", "in", self.ids)]
        )
        for rec in select:
            self.write({"is_visible": True})

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code_type} - {record.description}"


class CucuCatalogsPaymentMethod(models.Model):
    _name = "cucu.catalogs.payment.method"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    is_visible = fields.Boolean("Visible", default=False)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, payment_method):
        company_id = self.env.companies.id
        db_payment = self.env["cucu.catalogs.payment.method"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_payment) > 0:
            map_ids = list(map(lambda pos_id: pos_id["code_type"], db_payment))
            for rec in payment_method:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in payment_method:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_actives(self):
        select = self.env["cucu.catalogs.payment.method"].search(
            [("id", "in", self.ids)]
        )
        for rec in select:
            self.write({"is_visible": True})


class CucuCatalogsCurrency(models.Model):
    _name = "cucu.catalogs.currency"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    is_visible = fields.Boolean("Visible", default=False)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, currency):
        company_id = self.env.companies.id
        db_currency = self.env["cucu.catalogs.currency"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_currency) > 0:
            map_ids = list(map(lambda pos_id: pos_id["code_type"], db_currency))
            for rec in currency:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in currency:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.currency"].search([("id", "in", self.ids)])
        for rec in select:
            self.write({"is_visible": True})


class CucuCatalogsPointOfSale(models.Model):
    _name = "cucu.catalogs.point.of.sale"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    is_visible = fields.Boolean("Visible", default=True)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, pos):
        company_id = self.env.companies.id
        db_pos = self.env["cucu.catalogs.point.of.sale"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_pos) > 0:
            map_ids = list(map(lambda pos_id: pos_id["code_type"], db_pos))
            for rec in pos:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in pos:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.point.of.sale"].search(
            [("id", "in", self.ids)]
        )
        for rec in select:
            self.write({"is_visible": True})


class CucuCatalogsUnitMeasure(models.Model):
    _name = "cucu.catalogs.unit.measure"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    is_visible = fields.Boolean("Visible", default=False)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, unit_measure):
        company_id = self.env.companies.id
        db_unit = self.env["cucu.catalogs.unit.measure"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_unit) > 0:
            map_ids = list(map(lambda unit_db: unit_db["code_type"], db_unit))
            for rec in unit_measure:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in unit_measure:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.unit.measure"].search([("id", "in", self.ids)])
        for rec in select:
            self.write({"is_visible": True})


class CucuCatalogsMotiveCancel(models.Model):
    _name = "cucu.catalogs.cancel"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
    is_visible = fields.Boolean("Visible", default=True)
    company_id = fields.Many2one("res.company", "Company")

    def create_catalog(self, cancel_data):
        company_id = self.env.companies.id
        db_cancel = self.env["cucu.catalogs.cancel"].search(
            [("company_id", "=", company_id)]
        )
        if len(db_cancel) > 0:
            map_ids = list(map(lambda unit_db: unit_db["code_type"], db_cancel))
            for rec in cancel_data:
                if rec["codeType"] not in map_ids:
                    self._create_data(rec)
        else:
            for rec in cancel_data:
                self._create_data(rec)
        self.env.cr.commit()

    def _create_data(self, data):
        self.create(
            {
                "code_type": data["codeType"],
                "description": data["description"],
                "company_id": self.env.companies.id,
            }
        )

    def action_catalog_active(self):
        select = self.env["cucu.catalogs.cancel"].search([("id", "in", self.ids)])
        for rec in select:
            self.write({"is_visible": True})
