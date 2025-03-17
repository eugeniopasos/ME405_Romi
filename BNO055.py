from pyb import I2C, Pin, delay
from struct import unpack_from, calcsize
from micropython import const



class BNO055:
    DEV_ADDR = const(0x28)  # Device I2C address

    # Register addresses and data formats
    class reg:
        CHIP_ID =       (const(0x00), b"<B")   # Chip ID register
        OPR_MODE =      (const(0x3D), b"<B")   # Operation mode register
        PWR_MODE =      (const(0x3E), b"<B")   # Power mode register
        UNIT_SEL =      (const(0x3B), b"<B")   # Unit selection register
        SYS_TRIGGER =   (const(0x3F), b"<B")   # System trigger register
        CAL_STAT =      (const(0x35), b"<B")   # Calibration status register
        EUL_DATA_ALL =  (const(0x1A), b"<hhh") # Euler angles (heading, roll, pitch)
        ACC_DATA =      (const(0x08), b"<hhh") # Accelerometer data
        GYR_DATA =      (const(0x14), b"<hhh") # Gyroscope data
        MAG_DATA =      (const(0x0E), b"<hhh") # Magnetometer data
        
        # Calibration offset registers
        ACC_OFFSET =    (const(0x55), b"<hhhh") 
        MAG_OFFSET =    (const(0x5B), b"<hhhh") 
        GYR_OFFSET =    (const(0x61), b"<hhhh") 

    # Operating modes
    CONFIG_MODE = const(0x00)  # Configuration mode
    NDOF_MODE = const(0x0C)    # 9-DOF sensor fusion mode
    IMU_MODE = const(0x08)     # IMU mode (accelerometer + gyroscope)

    def __init__(self, SDA, SCL, RST, bus=2):
        # Initialize I2C pins
        self.SDA = Pin(SDA, mode=Pin.AF_OD, af=4)
        self.SCL = Pin(SCL, mode=Pin.AF_OD, af=4)
        self.RST = Pin(RST, mode=Pin.OUT_PP)

        # Reset the IMU
        self.RST.low()
        delay(10)
        self.RST.high()
        delay(700)  # Allow time for startup

        # Initialize I2C bus
        self.i2c = I2C(bus, I2C.CONTROLLER)
        self.i2c.init(I2C.CONTROLLER)  # Initialize as controller

        self._buf = const(22)  # Buffer size for reading data

    def _write_reg(self, reg, value):
        """ Write a value to a register """
        self.i2c.mem_write(value, self.DEV_ADDR, reg[0])

    def _read_reg(self, reg):
        """ Read data from a register and unpack it """
        length = calcsize(reg[1])
        buf = bytearray(length)
        self.i2c.mem_read(buf, self.DEV_ADDR, reg[0])
        return unpack_from(reg[1], buf)

    def change_mode(self, mode):
        """ Change the sensor's operation mode """
        self._write_reg(self.reg.OPR_MODE, self.CONFIG_MODE)
        delay(10)
        self._write_reg(self.reg.OPR_MODE, mode)
        delay(20)

    def get_calibrate_status(self):
        """ Get the current calibration status of the sensor """
        calib_stat = self._read_reg(self.reg.CAL_STAT)[0]
        return {
            "sys": (calib_stat >> 6) & 0x03,  # System calibration status
            "gyro": (calib_stat >> 4) & 0x03, # Gyroscope calibration status
            "accel": (calib_stat >> 2) & 0x03,# Accelerometer calibration status
            "mag": calib_stat & 0x03,         # Magnetometer calibration status
        }

    def get_calibrate_coeff(self):
        """ Read calibration offsets from the sensor """
        acc_offset = self._read_reg(self.reg.ACC_OFFSET)
        mag_offset = self._read_reg(self.reg.MAG_OFFSET)
        gyr_offset = self._read_reg(self.reg.GYR_OFFSET)
        return acc_offset, mag_offset, gyr_offset

    def write_calibrate_coeff(self, acc_offset, mag_offset, gyr_offset):
        """ Write calibration offsets to the sensor """
        self.change_mode(self.CONFIG_MODE)
        delay(10)
        self.i2c.mem_write(bytes(acc_offset), self.DEV_ADDR, self.reg.ACC_OFFSET[0])
        self.i2c.mem_write(bytes(mag_offset), self.DEV_ADDR, self.reg.MAG_OFFSET[0])
        self.i2c.mem_write(bytes(gyr_offset), self.DEV_ADDR, self.reg.GYR_OFFSET[0])
        self.change_mode(self.NDOF_MODE)
        delay(20)

    def read_euler(self):
        """ Read Euler angles (heading, roll, pitch) """
        head, roll, pitch = self._read_reg(self.reg.EUL_DATA_ALL)
        return head / 16, roll / 16, pitch / 16  # Convert to degrees

    def read_angular_velocity(self):
        """ Read angular velocity from the gyroscope """
        return self._read_reg(self.reg.GYR_DATA)

    def read_acceleration(self):
        """ Read acceleration data from the accelerometer """
        return self._read_reg(self.reg.ACC_DATA)

    def read_magnetic_field(self):
        """ Read magnetic field data from the magnetometer """
        return self._read_reg(self.reg.MAG_DATA)

    def initialize(self):
        """ Initialize and configure the BNO055 sensor """
        self.change_mode(self.CONFIG_MODE)
        delay(50)
        self._write_reg(self.reg.PWR_MODE, 0x00)  # Set power mode to normal
        self._write_reg(self.reg.UNIT_SEL, 0x00)  # Set default unit selection
        self.change_mode(self.NDOF_MODE)
        delay(50)
