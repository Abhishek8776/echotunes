from django.core.management.base import BaseCommand
from datetime import date
from PRODUCTS.models import Coupon
import schedule,time



def update_coupon_status_task():
  today = date.today()
  coupons = Coupon.objects.all()
  for coupon in coupons:
    if today < coupon.start_date:
      coupon.status = 'Upcoming'
    elif today <= coupon.end_date:
      coupon.status = 'Active'
    else:
      coupon.status = 'Expired'
    coupon.save()
  # print('working')


class Command(BaseCommand):
  help = 'Schedule update coupon status task'

  def handle(self, *args, **kwargs):
    schedule.every().day.at('00:00').do(update_coupon_status_task)
    # schedule.every(2).seconds.do(update_coupon_status_task)
    while True:
      schedule.run_pending()
      time.sleep(1)
