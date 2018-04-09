from ParkingLotServer import db


class StagingPriceUpdates(db.Model):
    __tablename__ = "staging_price_updates"

    id = db.Column(db.Integer, primary_key=True)
    # pl_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'))
    pl_id = db.Column(db.Integer, nullable=False)
    ch_id = db.Column(db.Integer, nullable=False)
    price_snapshot = db.Column(db.String(2500), nullable=False)
    ch_sent = db.Column(db.Boolean, default=False, nullable=False)
    update_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, pl_id, charge_id, price_snapshot):
        self.pl_id = pl_id
        self.ch_id = charge_id
        self.price_snapshot = price_snapshot
