"""Kiểm thử tự động cho bài tập tuần 4.

Sinh viên: Nguyễn Hải Đăng - Mã sinh viên: 202418863.
"""

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from decimal import Decimal

from main import (Employee, HourlyEmployee, Payroll, SalariedEmployee,
                  SalesEmployee)


def buildSampleEmployees():
    """Tạo mới bốn nhân sự mẫu cho mỗi tình huống."""
    e1 = SalariedEmployee("E001", "Nguyễn Minh An", "Đào tạo", 15000000, 2000000)
    e1.addBonus(1000000)
    e2 = HourlyEmployee("E002", "Trần Thu Bình", "Hỗ trợ", 100000, 150)
    e2.addBonus(500000, "Hoàn thành công việc")
    e3 = HourlyEmployee("E003", "Lê Hoàng Chi", "Hỗ trợ", 100000, 170)
    e4 = SalesEmployee("E004", "Phạm Quốc Dũng", "Kinh doanh",
                       8000000, 200000000, 0.05)
    e4.addBonus(0.02, 50000000, "Thưởng theo kết quả kinh doanh")
    return e1, e2, e3, e4


def buildSamplePayroll():
    payroll = Payroll("2026-10")
    for employee in buildSampleEmployees():
        payroll.addEmployee(employee)
    return payroll


class TestSampleData(unittest.TestCase):
    def test_gross_pay_of_each_employee(self):
        e1, e2, e3, e4 = buildSampleEmployees()
        self.assertEqual(e1.calculateGrossPay(), Decimal(18000000))
        self.assertEqual(e2.calculateGrossPay(), Decimal(15500000))
        self.assertEqual(e3.calculateGrossPay(), Decimal(17500000))
        self.assertEqual(e4.calculateGrossPay(), Decimal(19000000))

    def test_totals_and_lookup(self):
        payroll = buildSamplePayroll()
        self.assertEqual(payroll.calculateTotalPayroll(), Decimal(70000000))
        self.assertEqual(payroll.calculatePayrollByDepartment("Hỗ trợ"),
                         Decimal(33000000))
        self.assertEqual(payroll.findHighestPaidEmployee().employeeId, "E004")
        self.assertIs(payroll.findEmployee("E004"), payroll.employees[3])
        self.assertIsNone(payroll.findEmployee("E999"))

    def test_abstract_employee_and_types(self):
        with self.assertRaises(TypeError):
            Employee("X1", "Không tạo được")
        self.assertFalse(issubclass(Payroll, Employee))
        types = {e.getEmployeeType() for e in buildSampleEmployees()}
        self.assertEqual(len(types), 3)

    def test_display_runs_and_shows_components(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            buildSamplePayroll().displayPayroll()
        text = buffer.getvalue()
        self.assertIn("2026-10", text)
        self.assertIn("70.000.000 đồng", text)
        self.assertIn("Tiền hoa hồng: 10.000.000 đồng", text)
        self.assertIn("Giờ vượt 160", text)


class TestConstructors(unittest.TestCase):
    def test_T01_short_constructors(self):  # T01
        for cls in (SalariedEmployee, HourlyEmployee, SalesEmployee):
            with self.subTest(cls=cls.__name__):
                emp = cls("A1", "Tên")
                self.assertEqual(emp.department, "Unassigned")
                self.assertEqual(emp.monthlyBonus, Decimal(0))
                self.assertEqual(emp.calculateGrossPay(), Decimal(0))
        self.assertEqual(SalariedEmployee("A", "B").monthlySalary, 0)
        self.assertEqual(SalariedEmployee("A", "B").responsibilityAllowance, 0)
        self.assertEqual(HourlyEmployee("A", "B").hourlyRate, 0)
        self.assertEqual(HourlyEmployee("A", "B").workedHours, 0)
        sales = SalesEmployee("A", "B")
        self.assertEqual((sales.baseSalary, sales.salesRevenue,
                          sales.commissionRate), (0, 0, 0))

    def test_text_is_stripped(self):
        emp = SalariedEmployee("  E1 ", " An ", " Đào tạo ")
        self.assertEqual((emp.employeeId, emp.fullName, emp.department),
                         ("E1", "An", "Đào tạo"))

    def test_T04_invalid_text(self):  # T04
        for bad in ("", "   ", "\t\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    SalariedEmployee(bad, "Tên")
                with self.assertRaises(ValueError):
                    SalariedEmployee("A1", bad)
                with self.assertRaises(ValueError):
                    SalariedEmployee("A1", "Tên", bad)
        with self.assertRaises(TypeError):
            SalariedEmployee(123, "Tên")
        with self.assertRaises(ValueError):
            Payroll("  ")

    def test_number_type_checks(self):
        for bad in (True, "100", None, float("nan"), float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises((TypeError, ValueError)):
                    SalariedEmployee("A", "B", "C", bad, 0)
        with self.assertRaises(TypeError):
            SalariedEmployee("A", "B", "C", True, 0)
        with self.assertRaises(ValueError):
            SalariedEmployee("A", "B", "C", float("nan"), 0)
        # float được chuyển qua str nên không sinh sai số nhị phân
        emp = SalesEmployee("A", "B", "C", 0, 100, 0.1)
        self.assertEqual(emp.commissionRate, Decimal("0.1"))


class TestHourly(unittest.TestCase):
    def test_T02_boundaries(self):  # T02
        cases = [(0, 0), (160, 16000000), (250, 29500000),
                 (160.5, 16075000), (Decimal("160.5"), 16075000)]
        for hours, expected in cases:
            with self.subTest(hours=hours):
                emp = HourlyEmployee("H", "Giờ", "Hỗ trợ", 100000, hours)
                self.assertEqual(emp.calculateGrossPay(), Decimal(expected))

    def test_T03_invalid_hours(self):  # T03
        for hours in (-1, 251):
            with self.subTest(hours=hours):
                with self.assertRaises(ValueError):
                    HourlyEmployee("H", "Giờ", "Hỗ trợ", 100000, hours)

    def test_T05_negative_rate(self):
        with self.assertRaises(ValueError):
            HourlyEmployee("H", "Giờ", "Hỗ trợ", -1, 10)


class TestSalariedAndSales(unittest.TestCase):
    def test_T05_negative_values(self):  # T05
        with self.assertRaises(ValueError):
            SalariedEmployee("A", "B", "C", -1, 0)
        with self.assertRaises(ValueError):
            SalariedEmployee("A", "B", "C", 0, -1)
        with self.assertRaises(ValueError):
            SalesEmployee("A", "B", "C", -1, 0, 0)
        with self.assertRaises(ValueError):
            SalesEmployee("A", "B", "C", 0, -1, 0)

    def test_T05_update_sales_revenue(self):
        emp = SalesEmployee("S", "Bán", "KD", 1000000, 10000000, 0.1)
        emp.updateSalesRevenue(20000000)
        self.assertEqual(emp.salesRevenue, Decimal(20000000))
        self.assertEqual(emp.calculateGrossPay(), Decimal(3000000))
        with self.assertRaises(ValueError):
            emp.updateSalesRevenue(-1)
        with self.assertRaises(TypeError):
            emp.updateSalesRevenue("abc")
        self.assertEqual(emp.salesRevenue, Decimal(20000000))

    def test_T06_commission_rate(self):  # T06
        for rate in (0, 0.3, Decimal("0.3")):
            with self.subTest(rate=rate):
                SalesEmployee("S", "Bán", "KD", 0, 0, rate)
        for rate in (-0.01, 0.31):
            with self.subTest(rate=rate):
                with self.assertRaises(ValueError):
                    SalesEmployee("S", "Bán", "KD", 0, 0, rate)


class TestBonus(unittest.TestCase):
    def test_T07_accumulate_and_reset(self):  # T07
        emp = SalariedEmployee("A", "B")
        emp.addBonus(100000)
        self.assertEqual(emp.monthlyBonus, Decimal(100000))
        emp.addBonus(200000, "A")
        self.assertEqual(emp.monthlyBonus, Decimal(300000))
        emp.addBonus(0.02, 5000000, "B")
        self.assertEqual(emp.monthlyBonus, Decimal(400000))
        emp.resetMonthlyBonus()
        self.assertEqual(emp.monthlyBonus, Decimal(0))
        emp.addBonus(0.5, 1000, "Biên")
        self.assertEqual(emp.monthlyBonus, Decimal(500))

    def test_bonus_has_no_public_setter(self):
        emp = SalariedEmployee("A", "B")
        with self.assertRaises(AttributeError):
            emp.monthlyBonus = Decimal(5)
        with self.assertRaises(AttributeError):
            emp.employeeId = "Z"

    def test_T08_value_errors_keep_state(self):  # T08
        bad_calls = [
            (0,), (-5,), (0, "ok"), (-5, "ok"), (100, ""), (100, "   "),
            (0, 1000, "r"), (-0.1, 1000, "r"), (0.51, 1000, "r"),
            (0.1, 0, "r"), (0.1, -1000, "r"), (0.1, 1000, ""),
            (0.1, 1000, "  "),
        ]
        for args in bad_calls:
            with self.subTest(args=args):
                emp = SalariedEmployee("A", "B")
                emp.addBonus(7)
                with self.assertRaises(ValueError):
                    emp.addBonus(*args)
                self.assertEqual(emp.monthlyBonus, Decimal(7))

    def test_T08_type_errors_keep_state(self):  # T08
        bad_calls = [(), (1, "a", "b", "c"), ("100",), (True,), (100, 5),
                     (0.1, "x", "r"), (0.1, 1000, 5), (None,)]
        for args in bad_calls:
            with self.subTest(args=args):
                emp = SalariedEmployee("A", "B")
                emp.addBonus(7)
                with self.assertRaises(TypeError):
                    emp.addBonus(*args)
                self.assertEqual(emp.monthlyBonus, Decimal(7))


class TestPayroll(unittest.TestCase):
    def test_T09_duplicate_and_wrong_type(self):  # T09
        payroll = Payroll("2026-10")
        first = SalariedEmployee("E001", "An", "Đào tạo", 1, 1)
        second = HourlyEmployee("E001", "Khác", "Hỗ trợ", 1, 1)
        self.assertTrue(payroll.addEmployee(first))
        self.assertFalse(payroll.addEmployee(second))
        self.assertEqual(len(payroll.employees), 1)
        self.assertIs(payroll.findEmployee("E001"), first)
        for bad in ("E002", None, 5, object()):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    payroll.addEmployee(bad)
        self.assertEqual(len(payroll.employees), 1)

    def test_T10_empty_payroll(self):  # T10
        payroll = Payroll("2026-11")
        self.assertEqual(payroll.calculateTotalPayroll(), Decimal(0))
        self.assertEqual(payroll.calculatePayrollByDepartment("Hỗ trợ"),
                         Decimal(0))
        self.assertIsNone(payroll.findEmployee("E001"))
        self.assertIsNone(payroll.findHighestPaidEmployee())
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            payroll.displayPayroll()
        self.assertIn("rỗng", buffer.getvalue())

    def test_T10_unknown_department_and_tie(self):  # T10
        payroll = buildSamplePayroll()
        self.assertEqual(payroll.calculatePayrollByDepartment("Không có"),
                         Decimal(0))
        tie = Payroll("2026-10")
        a = SalariedEmployee("T1", "Một", "X", 5000000, 0)
        b = SalariedEmployee("T2", "Hai", "X", 5000000, 0)
        tie.addEmployee(a)
        tie.addEmployee(b)
        self.assertIs(tie.findHighestPaidEmployee(), a)

    def test_polymorphic_total_uses_updated_state(self):
        payroll = buildSamplePayroll()
        payroll.findEmployee("E004").updateSalesRevenue(0)
        self.assertEqual(payroll.calculateTotalPayroll(), Decimal(60000000))

    def test_import_does_not_run_main(self):
        # Import trong tiến trình riêng: không được tự in dữ liệu mẫu.
        result = subprocess.run(
            [sys.executable, "-c", "import main"],
            capture_output=True, text=True, encoding="utf-8",
            cwd=os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
