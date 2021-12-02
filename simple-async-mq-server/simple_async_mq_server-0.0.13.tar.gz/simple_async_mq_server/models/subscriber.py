class Subscriber:
  def __init__(self, topic, output_format, sid) -> None:
      self.topic = topic
      self.output_format = output_format
      self.sid = sid
      self.message_sent_count: int = 0


  def __repr__(self):
      return f'Topic: {self.topic}, Output format: {self.output_format}, SID: {self.sid}'
