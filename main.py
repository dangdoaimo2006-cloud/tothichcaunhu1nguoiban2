"""Bài tập tuần 4 - Hệ thống tính lương và thưởng nhân sự.

Sinh viên: Nguyễn Hải Đăng - Mã sinh viên: 202418863.
"""

import math
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional, Tuple

# ---------------------------------------------------------------------------
# Hàm kiểm tra dữ liệu dùng chung
# ---------------------------------------------------------------------------


def _clean_text(value: Any, field: str) -> str:
    """Kiểm tra chuỗi không rỗng sau strip() và trả về chuỗi đã strip."""
    if not isinstance(value, str):
        raise TypeError(f"{field} phải là chuỗi, nhận được {type(value).__name__}")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} không được rỗng")
    return cleaned


def _to_decimal(value: Any, field: str) -> Decimal:
    """Chuyển int/float/Decimal sang Decimal; loại bool, NaN và vô cực."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise TypeError(f"{field} phải là số, nhận được {type(value).__name__}")
    if isinstance(value, float):
        number = Decimal(str(value))  # không tạo Decimal trực tiếp từ float
    else:
        number = Decimal(value)
    if not number.is_finite():
        raise ValueError(f"{field} phải là số hữu hạn, nhận được {value}")
    return number


def _check_number(
    value: Any,
    field: str,
    minimum: Optional[Decimal] = None,
    maximum: Optional[Decimal] = None,
    minimum_exclusive: bool = False,
) -> Decimal:
    """Kiểm tra số nằm trong miền hợp lệ rồi trả về Decimal."""
    number = _to_decimal(value, field)
    if minimum is not None:
        if number < minimum or (minimum_exclusive and number == minimum):
            op = ">" if minimum_exclusive else ">="
            raise ValueError(f"{field} phải {op} {minimum}, nhận được {value}")
    if maximum is not None and number > maximum:
        raise ValueError(f"{field} phải <= {maximum}, nhận được {value}")
    return number


def formatMoney(amount: Decimal) -> str:
    """Định dạng tiền để hiển thị: làm tròn tới đồng, dấu chấm hàng nghìn."""
    rounded = int(amount.to_integral_value(rounding=ROUND_HALF_UP))
    return f"{rounded:,}".replace(",", ".") + " đồng"


def _formatNumber(value: Decimal) -> str:
    """Hiển thị số Decimal không có số mũ (150, 160.5, 0.05)."""
    return format(value.normalize(), "f")


# ---------------------------------------------------------------------------
# Lớp trừu tượng Employee
# ---------------------------------------------------------------------------


class Employee(ABC):
    """Lớp cơ sở trừu tượng cho mọi nhân sự."""

    UNASSIGNED = "Unassigned"

    def __init__(self, employeeId: str, fullName: str,
                 department: str = UNASSIGNED) -> None:
        """Dạng Employee(id, name) hoặc Employee(id, name, department)."""
        self._employeeId = _clean_text(employeeId, "employeeId")
        self._fullName = _clean_text(fullName, "fullName")
        self._department = _clean_text(department, "department")
        self._monthlyBonus = Decimal(0)

    @property
    def employeeId(self) -> str:
        return self._employeeId

    @property
    def fullName(self) -> str:
        return self._fullName

    @property
    def department(self) -> str:
        return self._department

    @property
    def monthlyBonus(self) -> Decimal:
        return self._monthlyBonus

    def addBonus(self, *args: Any) -> None:
        """Cộng thưởng; mô phỏng nạp chồng bằng số lượng đối số lúc chạy.

        addBonus(amount) | addBonus(amount, reason)
        addBonus(rate, referenceAmount, reason)
        """
        count = len(args)
        if count in (1, 2):
            amount = _check_number(args[0], "amount", Decimal(0),
                                   minimum_exclusive=True)
            if count == 2:
                _clean_text(args[1], "reason")  # chỉ kiểm tra, không lưu
            bonus = amount
        elif count == 3:
            rate = _check_number(args[0], "bonusRate", Decimal(0),
                                 Decimal("0.5"), minimum_exclusive=True)
            reference = _check_number(args[1], "referenceAmount", Decimal(0),
                                      minimum_exclusive=True)
            _clean_text(args[2], "reason")
            bonus = rate * reference
        else:
            raise TypeError(
                f"addBonus nhận 1, 2 hoặc 3 đối số, nhận được {count}")
        # Chỉ cập nhật trạng thái sau khi mọi kiểm tra đã đạt
        self._monthlyBonus += bonus

    def resetMonthlyBonus(self) -> None:
        """Đặt tổng thưởng về 0 khi bắt đầu kỳ mới."""
        self._monthlyBonus = Decimal(0)

    @abstractmethod
    def calculateGrossPay(self) -> Decimal:
        """Thu nhập trước khấu trừ."""

    @abstractmethod
    def getEmployeeType(self) -> str:
        """Tên loại nhân sự."""

    @abstractmethod
    def displayPayrollInfo(self) -> None:
        """In thông tin lương của nhân sự."""

    # Hàm in dùng chung cho phần đầu và phần cuối của mọi phiếu lương
    def _printHeader(self) -> None:
        print(f"[{self.getEmployeeType()}] {self.employeeId} - {self.fullName}")
        print(f"  Phòng ban: {self.department}")

    def _printFooter(self) -> None:
        print(f"  Tổng thưởng: {formatMoney(self.monthlyBonus)}")
        print(f"  Thu nhập trước khấu trừ: {formatMoney(self.calculateGrossPay())}")


# ---------------------------------------------------------------------------
# Các lớp nhân sự cụ thể
# ---------------------------------------------------------------------------


class SalariedEmployee(Employee):
    """Nhân viên lương cố định."""

    def __init__(self, employeeId: str, fullName: str,
                 department: str = Employee.UNASSIGNED,
                 monthlySalary: Any = 0,
                 responsibilityAllowance: Any = 0) -> None:
        salary = _check_number(monthlySalary, "monthlySalary", Decimal(0))
        allowance = _check_number(responsibilityAllowance,
                                  "responsibilityAllowance", Decimal(0))
        super().__init__(employeeId, fullName, department)
        self._monthlySalary = salary
        self._responsibilityAllowance = allowance

    @property
    def monthlySalary(self) -> Decimal:
        return self._monthlySalary

    @property
    def responsibilityAllowance(self) -> Decimal:
        return self._responsibilityAllowance

    def calculateGrossPay(self) -> Decimal:
        return (self._monthlySalary + self._responsibilityAllowance
                + self.monthlyBonus)

    def getEmployeeType(self) -> str:
        return "Nhân viên lương cố định"

    def displayPayrollInfo(self) -> None:
        self._printHeader()
        print(f"  Lương tháng: {formatMoney(self._monthlySalary)}")
        print(f"  Phụ cấp trách nhiệm: "
              f"{formatMoney(self._responsibilityAllowance)}")
        self._printFooter()


class HourlyEmployee(Employee):
    """Nhân viên theo giờ; giờ vượt 160 được nhân hệ số 1.5."""

    STANDARD_HOURS = Decimal(160)
    OVERTIME_MULTIPLIER = Decimal("1.5")
    MAX_HOURS = Decimal(250)

    def __init__(self, employeeId: str, fullName: str,
                 department: str = Employee.UNASSIGNED,
                 hourlyRate: Any = 0, workedHours: Any = 0) -> None:
        rate = _check_number(hourlyRate, "hourlyRate", Decimal(0))
        hours = _check_number(workedHours, "workedHours", Decimal(0),
                              self.MAX_HOURS)
        super().__init__(employeeId, fullName, department)
        self._hourlyRate = rate
        self._workedHours = hours

    @property
    def hourlyRate(self) -> Decimal:
        return self._hourlyRate

    @property
    def workedHours(self) -> Decimal:
        return self._workedHours

    # Các giá trị dưới đây được tính từ trạng thái, không lưu riêng
    @property
    def regularHours(self) -> Decimal:
        return min(self._workedHours, self.STANDARD_HOURS)

    @property
    def overtimeHours(self) -> Decimal:
        return max(self._workedHours - self.STANDARD_HOURS, Decimal(0))

    @property
    def regularPay(self) -> Decimal:
        return self.regularHours * self._hourlyRate

    @property
    def overtimePay(self) -> Decimal:
        return self.overtimeHours * self._hourlyRate * self.OVERTIME_MULTIPLIER

    def calculateGrossPay(self) -> Decimal:
        return self.regularPay + self.overtimePay + self.monthlyBonus

    def getEmployeeType(self) -> str:
        return "Nhân viên theo giờ"

    def displayPayrollInfo(self) -> None:
        self._printHeader()
        print(f"  Đơn giá giờ: {formatMoney(self._hourlyRate)}")
        print(f"  Giờ thường: {_formatNumber(self.regularHours)} giờ -> "
              f"{formatMoney(self.regularPay)}")
        print(f"  Giờ vượt 160 (x1.5): {_formatNumber(self.overtimeHours)} giờ -> "
              f"{formatMoney(self.overtimePay)}")
        self._printFooter()


class SalesEmployee(Employee):
    """Nhân viên kinh doanh: lương cơ bản + hoa hồng theo doanh số."""

    MAX_COMMISSION_RATE = Decimal("0.3")

    def __init__(self, employeeId: str, fullName: str,
                 department: str = Employee.UNASSIGNED,
                 baseSalary: Any = 0, salesRevenue: Any = 0,
                 commissionRate: Any = 0) -> None:
        base = _check_number(baseSalary, "baseSalary", Decimal(0))
        revenue = _check_number(salesRevenue, "salesRevenue", Decimal(0))
        rate = _check_number(commissionRate, "commissionRate", Decimal(0),
                             self.MAX_COMMISSION_RATE)
        super().__init__(employeeId, fullName, department)
        self._baseSalary = base
        self._salesRevenue = revenue
        self._commissionRate = rate

    @property
    def baseSalary(self) -> Decimal:
        return self._baseSalary

    @property
    def salesRevenue(self) -> Decimal:
        return self._salesRevenue

    @property
    def commissionRate(self) -> Decimal:
        return self._commissionRate

    @property
    def commission(self) -> Decimal:
        return self._salesRevenue * self._commissionRate

    def updateSalesRevenue(self, salesRevenue: Any) -> None:
        """Kiểm tra rồi mới cập nhật; lỗi thì giữ nguyên giá trị cũ."""
        self._salesRevenue = _check_number(salesRevenue, "salesRevenue",
                                           Decimal(0))

    def calculateGrossPay(self) -> Decimal:
        return self._baseSalary + self.commission + self.monthlyBonus

    def getEmployeeType(self) -> str:
        return "Nhân viên kinh doanh"

    def displayPayrollInfo(self) -> None:
        self._printHeader()
        print(f"  Lương cơ bản: {formatMoney(self._baseSalary)}")
        print(f"  Doanh số: {formatMoney(self._salesRevenue)}")
        print(f"  Tỷ lệ hoa hồng: {_formatNumber(self._commissionRate * 100)}%")
        print(f"  Tiền hoa hồng: {formatMoney(self.commission)}")
        self._printFooter()


# ---------------------------------------------------------------------------
# Bảng lương
# ---------------------------------------------------------------------------


class Payroll:
    """Bảng lương của một kỳ; lưu tham chiếu tới các đối tượng Employee."""

    def __init__(self, period: str) -> None:
        self._period = _clean_text(period, "period")
        self._employees: list = []  # danh sách duy nhất các Employee

    @property
    def period(self) -> str:
        return self._period

    @property
    def employees(self) -> Tuple[Employee, ...]:
        """Bản sao chỉ đọc của danh sách (vẫn là các đối tượng gốc)."""
        return tuple(self._employees)

    def addEmployee(self, employee: Employee) -> bool:
        """Thêm nhân sự; trả False nếu đã có cùng employeeId."""
        if not isinstance(employee, Employee):
            raise TypeError(
                f"employee phải là Employee, nhận được {type(employee).__name__}")
        if self.findEmployee(employee.employeeId) is not None:
            return False
        self._employees.append(employee)
        return True

    def findEmployee(self, employeeId: str) -> Optional[Employee]:
        """Trả chính đối tượng có mã tương ứng hoặc None."""
        target = _clean_text(employeeId, "employeeId")
        for employee in self._employees:
            if employee.employeeId == target:
                return employee
        return None

    def calculateTotalPayroll(self) -> Decimal:
        """Tổng thu nhập; mỗi nhân sự được gọi calculateGrossPay() một lần."""
        total = Decimal(0)
        for employee in self._employees:
            total += employee.calculateGrossPay()
        return total

    def calculatePayrollByDepartment(self, department: str) -> Decimal:
        """Tổng thu nhập của một phòng ban (0 nếu không có ai)."""
        target = _clean_text(department, "department")
        total = Decimal(0)
        for employee in self._employees:
            if employee.department == target:
                total += employee.calculateGrossPay()
        return total

    def findHighestPaidEmployee(self) -> Optional[Employee]:
        """Người thu nhập cao nhất; bằng nhau thì giữ người thêm trước."""
        best: Optional[Employee] = None
        best_pay = Decimal(0)
        for employee in self._employees:
            pay = employee.calculateGrossPay()
            if best is None or pay > best_pay:  # dùng > để giữ người đầu
                best, best_pay = employee, pay
        return best

    def displayPayroll(self) -> None:
        """In bảng lương bằng gọi đa hình displayPayrollInfo()."""
        print(f"BẢNG LƯƠNG KỲ {self._period}")
        if not self._employees:
            print("  (Bảng lương rỗng, chưa có nhân sự nào)")
        for employee in self._employees:
            employee.displayPayrollInfo()
        print(f"TỔNG BẢNG LƯƠNG: {formatMoney(self.calculateTotalPayroll())}")


# ---------------------------------------------------------------------------
# Chương trình minh họa
# ---------------------------------------------------------------------------


def main() -> None:
    payroll = Payroll("2026-10")

    print("1) Tạo nhân sự, cộng thưởng và thêm vào bảng lương")
    e1 = SalariedEmployee("E001", "Nguyễn Minh An", "Đào tạo",
                          15000000, 2000000)
    e1.addBonus(1000000)  # dạng 1: thưởng cố định
    e2 = HourlyEmployee("E002", "Trần Thu Bình", "Hỗ trợ", 100000, 150)
    e2.addBonus(500000, "Hoàn thành công việc")  # dạng 2: có lý do
    e3 = HourlyEmployee("E003", "Lê Hoàng Chi", "Hỗ trợ", 100000, 170)
    e4 = SalesEmployee("E004", "Phạm Quốc Dũng", "Kinh doanh",
                       8000000, 200000000, 0.05)
    e4.addBonus(0.02, 50000000, "Thưởng theo kết quả kinh doanh")  # dạng 3
    for employee in (e1, e2, e3, e4):
        print(f"  Thêm {employee.employeeId}: {payroll.addEmployee(employee)}")

    print("\n2) Hiển thị bảng lương đa hình")
    payroll.displayPayroll()

    print("\n3) Tổng bảng lương")
    print(f"  {formatMoney(payroll.calculateTotalPayroll())}")

    print("\n4) Tổng phòng Hỗ trợ")
    print(f"  {formatMoney(payroll.calculatePayrollByDepartment('Hỗ trợ'))}")

    print("\n5) Người có thu nhập cao nhất")
    top = payroll.findHighestPaidEmployee()
    if top is not None:
        print(f"  {top.employeeId} — {top.fullName} — "
              f"{formatMoney(top.calculateGrossPay())}")

    print("\n6) Tra cứu E004 và E999")
    for code in ("E004", "E999"):
        found = payroll.findEmployee(code)
        if found is None:
            print(f"  {code}: không tìm thấy")
        else:
            print(f"  {code}: {found.fullName} ({found.getEmployeeType()})")

    print("\n7) Thêm lại người cùng mã")
    duplicate = SalariedEmployee("E001", "Người trùng mã")
    print(f"  Kết quả: {payroll.addEmployee(duplicate)}")
    print(f"  Số lượng nhân sự: {len(payroll.employees)}")

    print("\n8) Bảng lương rỗng")
    Payroll("2026-11").displayPayroll()


if __name__ == "__main__":
    main()
