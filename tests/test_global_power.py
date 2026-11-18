import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import enrich_global_power as power


class GlobalPowerTests(unittest.TestCase):
    def test_monthly_values_and_annual_fallback(self):
        parameters={}
        for name in power.PARAMS:
            parameters[name]={month:1.0 for month in power.MONTHS}
        parameters["T2M"].pop("ANN",None)
        parsed=power.parse_payload({"properties":{"parameter":parameters}})
        self.assertEqual(parsed["annual_metrics"]["air_temperature_2m_c"],1.0)
        self.assertEqual(len(parsed["monthly"]),12)

    def test_driest_three_months_are_reported(self):
        parameters={}
        for name in power.PARAMS:
            parameters[name]={month:10.0 for month in power.MONTHS}
        for month,value in zip(power.MONTHS,[1,2,3,4,5,6,7,8,9,10,11,12]):
            parameters["PRECTOTCORR"][month]=value
        parsed=power.parse_payload({"properties":{"parameter":parameters}})
        self.assertEqual(parsed["derived"]["three_driest_climatology_months"],["JAN","FEB","MAR"])

    def test_missing_values_are_not_zeroed(self):
        parameters={name:{month:-999 for month in power.MONTHS} for name in power.PARAMS}
        parameters["T2M"]["JAN"]=12.5
        parsed=power.parse_payload({"properties":{"parameter":parameters}})
        self.assertEqual(parsed["monthly"][0]["air_temperature_2m_c"],12.5)
        self.assertIsNone(parsed["monthly"][1]["air_temperature_2m_c"])
        self.assertIsNone(parsed["derived"]["mean_diurnal_air_temperature_range_c"])
        self.assertIsNone(parsed["derived"]["monthly_mean_air_temperature_span_c"])
        self.assertEqual(parsed["derived"]["three_driest_climatology_months"],[])

    def test_missing_temperature_rejects_payload(self):
        parameters={name:{month:-999 for month in power.MONTHS} for name in power.PARAMS}
        with self.assertRaises(ValueError):
            power.parse_payload({"properties":{"parameter":parameters}})


if __name__=="__main__":
    unittest.main()
