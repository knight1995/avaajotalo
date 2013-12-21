from django.test import TestCase
from datetime import datetime, timedelta
from django.contrib.auth.models import User as AuthUser
from models import *
from otalo.surveys.models import *
import broadcast, tasks
from awaazde.streamit import streamit

class BcastTest(TestCase):
    INTERVAL_MINS = 10
    
    def setUp(self):
        d1 = Dialer.objects.create(base_number=5002, type=Dialer.TYPE_PRI, max_nums=10, max_parallel_out=4, dialstring_prefix='user/', interval_mins=self.INTERVAL_MINS)                
    
    def test_bcast(self):
        dialers = Dialer.objects.all()
        
        subjects = []
        for i in range(20):
            s = Subject.objects.create(name='s'+str(i), number=str(i))
            subjects.append(s)
        
        now = datetime.now()
        nextyear = now.year+1
        d = datetime(year=nextyear, month=1, day=1, hour=10, minute=40)
        
        # Create a template
        line = Line.objects.create(number='5002', name='TEST', language='eng')
        for dialer in dialers:
            line.dialers.add(dialer)
        template = Survey.objects.create(number=line.number, template=True, created_on=d, name='TEST_TEMPLATE')
        
        # create bcast
        result = tasks.regular_bcast.delay(line, template, subjects, 0, d)
        self.assertTrue(result.successful())
        
        # schedule bcasts
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
        
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 0)
         
        # complete some calls
        completed = [10,11,12,13,14]
        Call.objects.filter(subject__number__in=completed).update(complete=True, duration=60)
        self.assertEqual(Call.objects.filter(complete=True).count(), 5)
        