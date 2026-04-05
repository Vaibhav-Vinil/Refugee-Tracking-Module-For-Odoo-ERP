# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'refugee_family'
        )
        """
    )
    if not cr.fetchone()[0]:
        return
    cr.execute(
        """
        UPDATE refugee_family
        SET status = 'complete'
        WHERE status IN ('separated', 'partial')
        """
    )
