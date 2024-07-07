# import requests
from flask import jsonify
from apps.models import MarginOmset
from apps.utils.functions import refreshPPOB, refreshSocialMedia
from apps import db

def updateMargin(request_data):
    try:
        # Ambil nilai dari badan permintaan
        pulsa = request_data.get('pulsa')
        game = request_data.get('game')
        social_media = request_data.get('social_media')
        ewallet = request_data.get('ewallet')
        voucher = request_data.get('voucher')
        pln = request_data.get('pln')
        paket_data = request_data.get('paket_data')

        # Perbarui nilai di basis data MarginOmset
        margin = MarginOmset.query.first()  # Ambil objek margin pertama (asumsi hanya satu baris data)
        if margin:
            margin.pulsa = pulsa
            margin.game = game
            margin.social_media = social_media
            margin.ewallet = ewallet
            margin.voucher = voucher
            margin.pln = pln
            margin.paket_data = paket_data

            # Commit perubahan ke basis data
            db.session.commit()
            refreshPPOB()
            refreshSocialMedia()
            return {'status': 'success', 'message': 'Margin data updated successfully'}, 200
        else:
            return {'status': 'error', 'message': 'Margin data not found'}, 404

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
