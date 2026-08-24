from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('ipo', '0008_investorprofile_investment_horizon_and_more')]
    operations = [migrations.AlterField(model_name='investorprofile', name='persona', field=models.CharField(choices=[('conservative','Conservative'),('moderate','Moderate / Balanced'),('balanced','Balanced'),('growth','Growth'),('aggressive','Aggressive')], default='moderate', max_length=20))]
