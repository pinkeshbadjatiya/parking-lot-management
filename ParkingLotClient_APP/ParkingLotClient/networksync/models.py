from ParkingLotClient import db

class UtilizationStage(db.Model):
    __tablename__ = "utilization_stage"

    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer, db.ForeignKey('parkinglot.pl_id'))
    util_date = db.Column(db.Date, unique=True, nullable=False)
    util_per_hour = db.Column(db.String(175), nullable=False)
    rev_per_hour = db.Column(db.String(175), nullable=False)
    avg_util = db.Column(db.Float, nullable=False)
    total_rev = db.Column(db.Float, nullable=False)
    isSent = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, pl_id, util_date, util_per_hour, rev_per_hour, avg_util, total_rev, isSent):
        self.pl_id = pl_id
        self.util_date = util_date
        self.util_per_hour = util_per_hour
        self.rev_per_hour = rev_per_hour
        self.avg_util = avg_util
        self.total_rev = total_rev
        self.isSent = isSent
