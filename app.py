from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///metrics.db')
Base = declarative_base()

class VMetric(Base):
    __tablename__ = 'vm_metrics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    is_alive = Column(Boolean)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    data = request.json
    metric = VMetric(
        timestamp=datetime.fromisoformat(data['timestamp']),
        cpu_percent=data['cpu_percent'],
        memory_percent=data['memory_percent'],
        is_alive=data['is_alive']
    )
    session.add(metric)
    session.commit()
    return jsonify({"message": "Metrics received"}), 200

@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = session.query(VMetric).order_by(VMetric.timestamp.desc()).all()
    return render_template('metrics.html', metrics=metrics)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

