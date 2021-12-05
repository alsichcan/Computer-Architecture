#----------------------------------------------------------------
#
#  4190.308 Computer Architecture (Fall 2021)
#
#  Project #4: A 6-stage Pipelined RISC-V Simulator
#
#  November 25, 2021
#
#  Jin-Soo Kim (jinsoo.kim@snu.ac.kr)
#  Systems Software & Architecture Laboratory
#  Dept. of Computer Science and Engineering
#  Seoul National University
#
#----------------------------------------------------------------

import sys

from consts import *
from isa import *
from components import *
from program import *
from pipe import *


#--------------------------------------------------------------------------
#   Control signal table
#--------------------------------------------------------------------------

csignals = {
    LW     : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_ADD  , WB_MEM, REN_1, MEN_1, M_XRD, MT_W, ],
    SW     : [ Y, BR_N  , OP1_RS1, OP2_IMS, OEN_1, OEN_1, ALU_ADD  , WB_X  , REN_0, MEN_1, M_XWR, MT_W, ],
    AUIPC  : [ Y, BR_N  , OP1_PC,  OP2_IMU, OEN_0, OEN_0, ALU_ADD  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    LUI    : [ Y, BR_N  , OP1_X,   OP2_IMU, OEN_0, OEN_0, ALU_COPY2, WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ADDI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_ADD  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SLLI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SLL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLTI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SLT  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLTIU  : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SLTU , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    XORI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_XOR  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SRLI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SRL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SRAI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SRA  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ORI    : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_OR   , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ANDI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_AND  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ADD    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_ADD  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SUB    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SUB  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SLL    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SLL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLT    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SLT  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLTU   : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SLTU , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    XOR    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_XOR  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SRL    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SRL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SRA    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SRA  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    OR     : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_OR   , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    AND    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_AND  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    JALR   : [ Y, BR_JR , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_ADD  , WB_PC4, REN_1, MEN_0, M_X  , MT_X, ],   
    JAL    : [ Y, BR_J  , OP1_X,  OP2_IMJ, OEN_0, OEN_0, ALU_X    , WB_PC4, REN_1, MEN_0, M_X  , MT_X, ],

    BEQ    : [ Y, BR_EQ , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SEQ  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BNE    : [ Y, BR_NE , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SEQ  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BLT    : [ Y, BR_LT , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLT  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BGE    : [ Y, BR_GE , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLT  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BLTU   : [ Y, BR_LTU, OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLTU , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],

    BGEU   : [ Y, BR_GEU, OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLTU , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    ECALL  : [ Y, BR_N  , OP1_X  , OP2_X  , OEN_0, OEN_0, ALU_X    , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    EBREAK : [ Y, BR_N  , OP1_X  , OP2_X  , OEN_0, OEN_0, ALU_X    , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
}


#--------------------------------------------------------------------------
#   IF: Instruction fetch stage
#--------------------------------------------------------------------------

class IF(Pipe):

    # Pipeline registers ------------------------------

    reg_pc          = WORD(0)       # IF.reg_pc

    #--------------------------------------------------


    def __init__(self):
        super().__init__()
        self.bubble = False
        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.IF.pc
        #   self.inst               # Pipe.IF.inst
        #   self.exception          # Pipe.IF.exception
        #   self.pc_next            # Pipe.IF.pc_next
        #   self.pcplus4            # Pipe.IF.pcplus4
        #
        #----------------------------------------------

    def compute(self):
        # DO NOT TOUCH -----------------------------------------------
        # Read out pipeline register values 
        self.pc     = IF.reg_pc

        # Fetch an instruction from instruction memory (imem)
        self.inst, status = Pipe.cpu.imem.access(True, self.pc, 0, M_XRD)

        # Handle exception during imem access
        if not status:
            self.exception = EXC_IMEM_ERROR
            self.inst = BUBBLE
        else:
            self.exception = EXC_NONE
        #-------------------------------------------------------------

        if self.bubble:
            return

        # Compute PC + 4 using an adder
        self.pcplus4    = Pipe.cpu.adder_pcplus4.op(self.pc, 4)
        self.pc_next = self.pcplus4

        # Use Pipe.cpu.adder_if if you need an additional adder
        # Branch Prediction
        opcode = RISCV.opcode(self.inst)
        cs = csignals[opcode]
        c_br_type = cs[CS_BR_TYPE]  # Branch Type
        c_op2_sel  = cs[CS_OP2_SEL] # IMM value

        if c_br_type != BR_N:
            imm             = RISCV.imm_i(self.inst)   if c_op2_sel == OP2_IMI      else \
                              RISCV.imm_b(self.inst)   if c_op2_sel == OP2_IMB      else \
                              RISCV.imm_j(self.inst)   if c_op2_sel == OP2_IMJ      else \
                              WORD(0)

            # Use Pipe.cpu.ras for the return address stack
            if c_br_type == BR_J:
                # Jal Instruction - Always Taken
                self.pc_next = Pipe.cpu.adder_if.op(self.pc, imm)
                if RISCV.rd(self.inst) == 1:
                    Pipe.cpu.rastack.push(self.pcplus4)
            elif c_br_type == BR_JR:
                # Jalr Instruction - Always Not Taken
                self.pc_next = self.pcplus4

                if RISCV.rd(self.inst) == 1:
                    Pipe.cpu.rastack.push(self.pcplus4)

                if RISCV.rd(self.inst) == 0 and \
                    RISCV.rs1(self.inst) == 1 and \
                    imm == 0:
                    self.pc_next, status = Pipe.cpu.rastack.pop()
            else:
                if imm < 0:
                    # Backward branch - Taken
                    self.pc_next = Pipe.cpu.adder_if.op(self.pc, imm)
                else:
                    # Forward branch - Not Taken
                    self.pc_next = self.pcplus4

    def update(self):

        if self.bubble:
            IF.reg_pc           = self.pc_next
            ID.reg_pc           = self.pc
            ID.reg_inst         = WORD(BUBBLE)
            ID.reg_exception    = self.exception
            self.bubble         = False
        elif not Pipe.ID.IF_stall:
            IF.reg_pc           = self.pc_next
            ID.reg_pc           = self.pc
            ID.reg_inst         = self.inst
            ID.reg_exception    = self.exception
        else:
            Pipe.ID.IF_stall = False

        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_IF, self.pc, self.inst, self.log())
        #-------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        return("# inst=0x%08x, pc_next=0x%08x" % (self.inst, self.pc_next))
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   ID: Instruction decode stage
#--------------------------------------------------------------------------

class ID(Pipe):


    # Pipeline registers ------------------------------

    reg_pc          = WORD(0)           # ID.reg_pc
    reg_inst        = WORD(BUBBLE)      # ID.reg_inst
    reg_exception   = WORD(EXC_NONE)    # ID.reg_exception

    #--------------------------------------------------

    
    def __init__(self):
        super().__init__()
        self.bubble = False
        self.IF_stall = False
        self.ID_stall = False

        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.ID.pc
        #   self.inst               # Pipe.ID.inst
        #   self.exception          # Pipe.ID.exception
        #
        #   self.rs1                # Pipe.ID.rs1
        #   self.rs2                # Pipe.ID.rs2
        #   self.rd                 # Pipe.ID.rd
        #   self.c_br_type          # Pipe.ID.c_br_type
        #   self.c_op1_sel          # Pipe.ID.c_op1_sel
        #   self.c_op2_sel          # Pipe.ID.c_op2_sel
        #   self.c_alu_fun          # Pipe.ID.c_alu_fun
        #   self.c_wb_sel           # Pipe.ID.c_wb_sel
        #   self.c_rf_wen           # Pipe.ID.c_rf_wen
        #   self.c_dmem_en          # Pipe.ID.c_dmem_en
        #   self.c_dmem_rw          # Pipe.ID.c_dmem_rw
        #   self.c_rs1_oen          # Pipe.ID.c_rs1_oen
        #   self.c_rs2_oen          # Pipe.ID.c_rs2_oen
        #   self.op1_data           # Pipe.ID.op1_data
        #   self.op2_data           # Pipe.ID.op2_data
        #   self.rs2_data           # Pipe.ID.rs2_data
        #
        #   self.M1_bubble          # Pipe.ID.M1_bubble
        #
        #----------------------------------------------


    def compute(self):
        # Readout pipeline register values
        self.pc         = ID.reg_pc
        self.inst       = ID.reg_inst
        self.exception  = ID.reg_exception

        self.rs1        = RISCV.rs1(self.inst)
        self.rs2        = RISCV.rs2(self.inst)
        self.rd         = RISCV.rd(self.inst)

        imm_i           = RISCV.imm_i(self.inst)
        imm_s           = RISCV.imm_s(self.inst)
        imm_b           = RISCV.imm_b(self.inst)
        imm_u           = RISCV.imm_u(self.inst)
        imm_j           = RISCV.imm_j(self.inst)


        # Generate control signals

        # DO NOT TOUCH------------------------------------------------
        opcode          = RISCV.opcode(self.inst)
        if opcode in [ EBREAK, ECALL ]:
            self.exception |= EXC_EBREAK
        elif opcode == ILLEGAL:
            self.exception |= EXC_ILLEGAL_INST
            self.inst = BUBBLE
            opcode = RISCV.opcode(self.inst)

        cs = csignals[opcode]
        self.c_br_type  = cs[CS_BR_TYPE] # Branch Type
        self.c_op1_sel  = cs[CS_OP1_SEL] # Operand Selector for ALU op1
        self.c_op2_sel  = cs[CS_OP2_SEL] # Operand Selector for ALU op2
        self.c_alu_fun  = cs[CS_ALU_FUN] # ALU Function Controller
        self.c_wb_sel   = cs[CS_WB_SEL]  # Write Data에 쓰일 Data의 MUX Signal
        self.c_rf_wen   = cs[CS_RF_WEN]  # RegWrite Enable Signal
        self.c_dmem_en  = cs[CS_MEM_EN]  # DataMemory Enable Signal
        self.c_dmem_rw  = cs[CS_MEM_FCN] # DataMemory Read/Write Signal
        self.c_rs1_oen  = cs[CS_RS1_OEN] # Operand Enable signal for rs1
        self.c_rs2_oen  = cs[CS_RS2_OEN] # Operand Enable signal for rs2

        # Any instruction with an exception becomes BUBBLE as it enters the M1 stage. (except EBREAK)
        # All the following instructions after exception become BUBBLEs too.
        self.M1_bubble = (Pipe.EX.exception and (Pipe.EX.exception != EXC_EBREAK)) or (Pipe.M1.exception)
        #-------------------------------------------------------------

        # Read register file
        rf_rs1_data     = Pipe.cpu.rf.read(self.rs1)  if self.c_rs1_oen == OEN_1   else WORD(0)
        rf_rs2_data     = Pipe.cpu.rf.read(self.rs2)  if self.c_rs2_oen == OEN_1   else WORD(0)


        # TODO : M1-M2 Hazard
        if self.c_dmem_en and Pipe.EX.c_dmem_en:
            self.IF_stall = True
            self.ID_stall = True

        # TODO : Read-After-Write Hazard
        if (Pipe.EX.c_rf_wen and (Pipe.EX.rd != 0)) \
                and (Pipe.EX.rd == self.rs1):
            rf_rs1_data = Pipe.EX.alu_out
        elif (Pipe.M1.c_rf_wen and (Pipe.M1.rd != 0)) \
                and (Pipe.M1.rd == self.rs1):
            rf_rs1_data = Pipe.M1.alu_out
        elif (Pipe.M2.c_rf_wen and (Pipe.M2.rd != 0)) \
                and (Pipe.M2.rd == self.rs1):
            rf_rs1_data = Pipe.M2.wbdata
        elif (Pipe.WB.c_rf_wen and (Pipe.WB.rd != 0)) \
                and (Pipe.WB.rd == self.rs1):
            rf_rs1_data = Pipe.WB.wbdata

        if (Pipe.EX.c_rf_wen and (Pipe.EX.rd != 0)) \
                and (Pipe.EX.rd == self.rs2):
            rf_rs2_data = Pipe.EX.alu_out
        elif (Pipe.M1.c_rf_wen and (Pipe.M1.rd != 0)) \
                and (Pipe.M1.rd == self.rs2):
            rf_rs2_data = Pipe.M1.wbdata
        elif (Pipe.M2.c_rf_wen and (Pipe.M2.rd != 0)) \
                and (Pipe.M2.rd == self.rs2):
            rf_rs2_data = Pipe.M2.wbdata
        elif (Pipe.WB.c_rf_wen and (Pipe.WB.rd != 0)) \
             and (Pipe.WB.rd == self.rs1):
            rf_rs2_data = Pipe.WB.wbdata

        # TODO : Load-Use Hazard Detection Unit - Stall & Bubble
        if (Pipe.EX.reg_c_dmem_en and Pipe.EX.reg_c_dmem_rw == M_XRD) and \
                (Pipe.EX.reg_rd == self.rs1 or Pipe.EX.reg_rd == self.rs2):
            self.IF_stall = True
            self.ID_stall = True
        elif (Pipe.M1.reg_c_dmem_en and Pipe.M1.reg_c_dmem_rw == M_XRD) and \
                (Pipe.M1.reg_rd == self.rs1 or Pipe.M1.reg_rd == self.rs2):
            self.IF_stall = True
            self.ID_stall = True
        elif (Pipe.M2.reg_c_dmem_en and Pipe.M2.reg_c_dmem_rw == M_XRD):
            if Pipe.M2.reg_rd == self.rs1:
                rf_rs1_data = Pipe.M2.wbdata

            if Pipe.M2.reg_rd == self.rs2:
                rf_rs2_data = Pipe.M2.wbdata

        # op1_sel signal에 따라 op1_data (rs1 or pc) 설정
        self.op1_data   = rf_rs1_data   if self.c_op1_sel == OP1_RS1      else \
                          self.pc       if self.c_op1_sel == OP1_PC       else \
                          WORD(0)

        self.rs2_data   = rf_rs2_data

        # op2_sel signal에 따라 op2_data (immediate) 설정
        self.op2_data   = rf_rs2_data   if self.c_op2_sel == OP2_RS2      else \
                          imm_i         if self.c_op2_sel == OP2_IMI      else \
                          imm_s         if self.c_op2_sel == OP2_IMS      else \
                          imm_u         if self.c_op2_sel == OP2_IMU      else \
                          imm_j         if self.c_op2_sel == OP2_IMJ      else \
                          imm_b         if self.c_op2_sel == OP2_IMB      else \
                          WORD(0)
    
    def update(self):
        EX.reg_pc = self.pc
        EX.reg_exception = self.exception

        if self.bubble:
            EX.reg_inst             = WORD(BUBBLE)
            EX.reg_c_wb_sel         = False
            EX.reg_c_alu_fun        = False
            EX.reg_c_rf_wen         = False
            EX.reg_c_dmem_en        = False
            EX.reg_c_dmem_rw        = False
            self.bubble             = False
        elif not self.ID_stall:
            EX.reg_inst             = self.inst
            EX.reg_rd               = self.rd
            EX.reg_op1_data         = self.op1_data
            EX.reg_op2_data         = self.op2_data
            EX.reg_rs2_data         = self.rs2_data
            EX.reg_c_br_type        = self.c_br_type
            EX.reg_c_wb_sel         = self.c_wb_sel
            EX.reg_c_alu_fun        = self.c_alu_fun
            EX.reg_c_rf_wen         = self.c_rf_wen
            EX.reg_c_dmem_en        = self.c_dmem_en
            EX.reg_c_dmem_rw        = self.c_dmem_rw
        else:
            EX.reg_inst             = WORD(BUBBLE)
            EX.reg_c_br_type        = False
            EX.reg_c_wb_sel         = False
            EX.reg_c_alu_fun        = False
            EX.reg_c_rf_wen         = False
            EX.reg_c_dmem_en        = False
            EX.reg_c_dmem_rw        = False
            self.ID_stall           = False

        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_ID, self.pc, self.inst, self.log())
        #-------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        if self.inst in [ BUBBLE, ILLEGAL ]:
            return('# -')
        else:
            return("# rd=%d rs1=%d rs2=%d op1=0x%08x op2=0x%08x"
                    % (self.rd, self.rs1, self.rs2, self.op1_data, self.op2_data))
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   EX: Execution stage
#--------------------------------------------------------------------------

class EX(Pipe):

    # Pipeline registers ------------------------------

    reg_pc              = WORD(0)           # EX.reg_pc
    reg_inst            = WORD(BUBBLE)      # EX.reg_inst
    reg_exception       = WORD(EXC_NONE)    # EX.reg_exception
    reg_rd              = WORD(0)           # EX.reg_rd
    reg_op1_data        = WORD(0)           # EX.reg_op1_data
    reg_op2_data        = WORD(0)           # EX.reg_op2_data
    reg_rs2_data        = WORD(0)           # EX.reg_rs2_data
    reg_c_br_type       = WORD(BR_N)        # EX.reg_c_br_type
    reg_c_wb_sel        = WORD(WB_X)        # EX.reg_c_wb_sel
    reg_c_alu_fun       = WORD(ALU_X)       # EX.reg_c_alu_fun
    reg_c_rf_wen        = False             # EX.reg_c_rf_wen
    reg_c_dmem_en       = False             # EX.reg_c_dmem_en
    reg_c_dmem_rw       = WORD(M_X)         # EX.reg_c_dmem_rw

    #--------------------------------------------------


    def __init__(self):
        super().__init__()
        self.bubble = False
        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.EX.pc
        #   self.inst               # Pipe.EX.inst
        #   self.exception          # Pipe.EX.exception
        #   self.rd                 # Pipe.EX.rd
        #   self.op1_data           # Pipe.EX.op1_data
        #   self.op2_data           # Pipe.EX.op2_data
        #   self.rs2_data           # Pipe.EX.rs2_data
        #   self.c_wb_sel           # Pipe.EX.c_wb_sel
        #   self.c_alu_fun          # Pipe.EX.c_alu_fun
        #   self.c_rf_wen           # Pipe.EX.c_rf_wen
        #   self.c_dmem_en          # Pipe.EX.c_dmem_en
        #   self.c_dmem_rw          # Pipe.EX.c_dmem_rw
        #
        #   self.alu_out            # Pipe.EX.alu_out
        #   self.alu2_data          # Pipe.EX.alu2_data
        #
        #----------------------------------------------


    def compute(self):
        # Read out pipeline register values
        self.pc                 = EX.reg_pc
        self.inst               = EX.reg_inst
        self.exception          = EX.reg_exception
        self.rd                 = EX.reg_rd
        self.op1_data           = EX.reg_op1_data
        self.op2_data           = EX.reg_op2_data
        self.rs2_data           = EX.reg_rs2_data
        self.c_br_type          = EX.reg_c_br_type
        self.c_wb_sel           = EX.reg_c_wb_sel
        self.c_alu_fun          = EX.reg_c_alu_fun
        self.c_rf_wen           = EX.reg_c_rf_wen
        self.c_dmem_en          = EX.reg_c_dmem_en
        self.c_dmem_rw          = EX.reg_c_dmem_rw

        # The second input to ALU should be put into self.alu2_data for correct log msg.
        self.alu2_data          = self.op2_data  if self.c_br_type != BR_N else\
                                  self.rs2_data



        # Perform ALU operation
        self.alu_out = Pipe.cpu.alu.op(self.c_alu_fun, self.op1_data, self.alu2_data)



        # Branch Verification
        if self.c_br_type != BR_N:
            if self.c_br_type == BR_JR:
                # Jalr Instruction - Always Not Taken
                if Pipe.ID.reg_pc != self.alu_out:
                    # Mispredicted
                    IF.pc_next = self.alu_out
                    Pipe.ID.bubble = True
                    Pipe.IF.bubble = True
            else:
                if self.op2_data < 0:
                    # Backward branch - Taken
                    if (self.c_br_type == BR_EQ and self.alu_out != 1) or \
                        (self.c_br_type == BR_NE and self.alu_out != 0) or \
                        (self.c_br_type == BR_LT and self.alu_out != 1) or \
                        (self.c_br_type == BR_GE and self.alu_out != 0) or \
                        (self.c_br_type == BR_LTU and self.alu_out != 1) or \
                        (self.c_br_type == BR_GEU and self.alu_out != 0):

                        IF.pc_next = Pipe.cpu.adder_pcplus4.op(self.pc)
                        Pipe.ID.bubble = True
                        Pipe.IF.bubble = True
                else:
                    # Forward branch - Not Taken
                    if (self.c_br_type == BR_EQ and self.alu_out == 1) or \
                        (self.c_br_type == BR_NE and self.alu_out == 0) or \
                        (self.c_br_type == BR_LT and self.alu_out == 1) or \
                        (self.c_br_type == BR_GE and self.alu_out == 0) or \
                        (self.c_br_type == BR_LTU and self.alu_out == 1) or \
                        (self.c_br_type == BR_GEU and self.alu_out == 0):

                        IF.pc_next = Pipe.cpu.adder_if.op(self.pc, self.op2_data)
                        Pipe.ID.bubble = True
                        Pipe.IF.bubble = True

    def update(self):

        M1.reg_pc               = self.pc
        M1.reg_exception        = self.exception

        if Pipe.ID.M1_bubble:
            M1.reg_inst         = WORD(BUBBLE)
            M1.reg_c_rf_wen     = False
            M1.reg_c_dmem_en    = False
        elif self.bubble:
            M1.reg_inst         = WORD(BUBBLE)
            M1.reg_c_rf_wen     = False
            M1.reg_c_dmem_en    = False
            self.bubble = False
        else:
            M1.reg_inst         = self.inst
            M1.reg_rd           = self.rd
            M1.reg_rs2_data     = self.rs2_data
            M1.reg_c_wb_sel     = self.c_wb_sel
            M1.reg_c_rf_wen     = self.c_rf_wen
            M1.reg_c_dmem_en    = self.c_dmem_en
            M1.reg_c_dmem_rw    = self.c_dmem_rw
            M1.reg_alu_out      = self.alu_out


        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_EX, self.pc, self.inst, self.log())
        #-------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):

        ALU_OPS = {
            ALU_X       : f'# -',
            ALU_ADD     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} + {self.alu2_data:#010x}',
            ALU_SUB     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} - {self.alu2_data:#010x}',
            ALU_AND     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} & {self.alu2_data:#010x}',
            ALU_OR      : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} | {self.alu2_data:#010x}',
            ALU_XOR     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} ^ {self.alu2_data:#010x}',
            ALU_SLT     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} < {self.alu2_data:#010x} (signed)',
            ALU_SLTU    : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} < {self.alu2_data:#010x} (unsigned)',
            ALU_SLL     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} << {self.alu2_data & 0x1f}',
            ALU_SRL     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} >> {self.alu2_data & 0x1f} (logical)',
            ALU_SRA     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} >> {self.alu2_data & 0x1f} (arithmetic)',
            ALU_COPY1   : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} (pass 1)',
            ALU_COPY2   : f'# {self.alu_out:#010x} <- {self.alu2_data:#010x} (pass 2)',
            ALU_SEQ     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} == {self.alu2_data:#010x}',
        }
        return('# -' if self.inst == BUBBLE else ALU_OPS[self.c_alu_fun]);
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   M1: Memory access stage 1
#--------------------------------------------------------------------------

class M1(Pipe):

    # Pipeline registers ------------------------------

    reg_pc              = WORD(0)           # M1.reg_pc
    reg_inst            = WORD(BUBBLE)      # M1.reg_inst
    reg_exception       = WORD(EXC_NONE)    # M1.reg_exception
    reg_rd              = WORD(0)           # M1.reg_rd
    reg_rs2_data        = WORD(0)           # M1.reg_rs2_data
    reg_c_wb_sel        = WORD(WB_X)        # M1.reg_c_wb_sel
    reg_c_rf_wen        = False             # M1.reg_c_rf_wen
    reg_c_dmem_en       = False             # M1.reg_c_dmem_en
    reg_c_dmem_rw       = WORD(M_X)         # M1.reg_c_dmem_rw
    reg_alu_out         = WORD(0)           # M1.reg_alu_out

    #--------------------------------------------------

    def __init__(self):
        super().__init__()
        self.bubble = False
        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.M1.pc
        #   self.inst               # Pipe.M1.inst
        #   self.exception          # Pipe.M1.exception
        #   self.rd                 # Pipe.M1.rd
        #   self.rs2_data           # Pipe.M1.rs2_data
        #   self.c_wb_sel           # Pipe.M1.c_wb_sel
        #   self.c_rf_wen           # Pipe.M1.c_rf_wen
        #   self.c_dmem_en          # Pipe.M1.c_dmem_en
        #   self.c_dmem_rw          # Pipe.M1.c_dmem_rw
        #   self.alu_out            # Pipe.M1.alu_out
        #
        #----------------------------------------------

    def compute(self):
        # Read out pipeline register values
        self.pc             = M1.reg_pc
        self.inst           = M1.reg_inst
        self.exception      = M1.reg_exception
        self.rd             = M1.reg_rd
        self.rs2_data       = M1.reg_rs2_data
        self.c_wb_sel       = M1.reg_c_wb_sel
        self.c_rf_wen       = M1.reg_c_rf_wen
        self.c_dmem_en      = M1.reg_c_dmem_en
        self.c_dmem_rw      = M1.reg_c_dmem_rw
        self.alu_out        = M1.reg_alu_out  

        if M1.reg_inst == WORD(BUBBLE):
            self.bubble = True
            return

        # DO NOT TOUCH -----------------------------------------------
        # Access dmem usign access2(): MM_STAGE1
        mem_data, status = Pipe.cpu.dmem.access2(self.c_dmem_en, self.alu_out, self.rs2_data, \
                                                 self.c_dmem_rw, self.pc, MM_STAGE1)

        # Handle exception during dmem access
        if not status:
            self.exception |= EXC_DMEM_ERROR
            self.c_rf_wen = False
        #-------------------------------------------------------------


    def update(self):

        M2.reg_pc = self.pc
        M2.reg_exception    = self.exception

        if self.bubble:
            M2.reg_inst = WORD(BUBBLE)
            M2.reg_c_dmem_en = False
            M2.reg_c_dmem_rw = False
            self.bubble = False
        else:
            M2.reg_inst         = self.inst
            M2.reg_rd           = self.rd
            M2.reg_rs2_data     = self.rs2_data
            M2.reg_c_wb_sel     = self.c_wb_sel
            M2.reg_c_rf_wen     = self.c_rf_wen
            M2.reg_c_dmem_en    = self.c_dmem_en
            M2.reg_c_dmem_rw    = self.c_dmem_rw
            M2.reg_alu_out      = self.alu_out


        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_M1, self.pc, self.inst, self.log())
        #-------------------------------------------------------------

    
    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        if not self.c_dmem_en:
            return('# -')
        elif self.c_dmem_rw == M_XRD:
            return('# loading from M[0x%08x]' % self.alu_out)
        else:
            return('# storing to M[0x%08x]' % self.alu_out)
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   M2: Memory access stage 2
#--------------------------------------------------------------------------

class M2(Pipe):

    # Pipeline registers ------------------------------

    reg_pc              = WORD(0)           # M2.reg_pc
    reg_inst            = WORD(BUBBLE)      # M2.reg_inst
    reg_exception       = WORD(EXC_NONE)    # M2.reg_exception
    reg_rd              = WORD(0)           # M2.reg_rd
    reg_rs2_data        = WORD(0)           # M2.reg_rs2_data
    reg_c_wb_sel        = WORD(WB_X)        # M2.reg_c_wb_sel
    reg_c_rf_wen        = False             # M2.reg_c_rf_wen
    reg_c_dmem_en       = False             # M2.reg_c_dmem_en
    reg_c_dmem_rw       = WORD(M_X)         # M2.reg_c_dmem_rw
    reg_alu_out         = WORD(0)           # M2.reg_alu_out

    #--------------------------------------------------

    def __init__(self):
        super().__init__()
        self.bubble = False
        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.M2.pc
        #   self.inst               # Pipe.M2.inst
        #   self.exception          # Pipe.M2.exception
        #   self.rd                 # Pipe.M2.rd
        #   self.rs2_data           # Pipe.M2.rs2_data
        #   self.c_wb_sel           # Pipe.M2.c_wb_sel
        #   self.c_rf_wen           # Pipe.M2.c_rf_wen
        #   self.c_dmem_en          # Pipe.M2.c_dmem_en
        #   self.c_dmem_rw          # Pipe.M2.c_dmem_rw
        #   self.alu_out            # Pipe.M2.alu_out
        #
        #   self.wbdata             # Pipe.M2.wbdata
        #
        #----------------------------------------------

    def compute(self):
        # Read out pipeline register values
        self.pc             = M2.reg_pc
        self.inst           = M2.reg_inst
        self.exception      = M2.reg_exception
        self.rd             = M2.reg_rd
        self.rs2_data       = M2.reg_rs2_data
        self.c_wb_sel       = M2.reg_c_wb_sel
        self.c_rf_wen       = M2.reg_c_rf_wen
        self.c_dmem_en      = M2.reg_c_dmem_en
        self.c_dmem_rw      = M2.reg_c_dmem_rw
        self.alu_out        = M2.reg_alu_out  

        # Check BUBBLE
        if M2.reg_inst == WORD(BUBBLE):
            self.bubble = True
            return

        # DO NOT TOUCH -----------------------------------------------
        # Access dmem usign access2(): MM_STAGE2
        mem_data, status = Pipe.cpu.dmem.access2(self.c_dmem_en, self.alu_out, self.rs2_data, \
                                                 self.c_dmem_rw, self.pc, MM_STAGE2)

        # Handle exception during dmem access
        if not status:
            self.exception |= EXC_DMEM_ERROR
            self.c_rf_wen = False

        # For load instruction, we need to store the value read from dmem
        # TODO : Check whether Changed value affects result
        self.wbdata         = mem_data        if self.c_wb_sel == WB_MEM else \
                              self.alu_out    if self.c_wb_sel == WB_ALU else \
                              Pipe.IF.pcplus4 if self.c_wb_sel == WB_PC4 else \
                              WORD(0)
        #-------------------------------------------------------------
        

    def update(self):
        WB.reg_pc           = self.pc
        WB.reg_exception    = self.exception

        if self.bubble:
            WB.reg_inst = WORD(BUBBLE)
            WB.reg_c_rf_wen = False
            self.bubble = False
        else:
            WB.reg_inst         = self.inst
            WB.reg_rd           = self.rd
            WB.reg_c_rf_wen     = self.c_rf_wen
            WB.reg_wbdata       = self.wbdata

        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_M2, self.pc, self.inst, self.log())
        #-------------------------------------------------------------

    
    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        if not self.c_dmem_en:
            return('# -')
        elif self.c_dmem_rw == M_XRD:
            return('# 0x%08x <- M[0x%08x]' % (self.wbdata, self.alu_out))
        else:
            return('# M[0x%08x] <- 0x%08x' % (self.alu_out, self.rs2_data))
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   WB: Write back stage
#--------------------------------------------------------------------------

class WB(Pipe):

    # Pipeline registers ------------------------------

    reg_pc              = WORD(0)           # WB.reg_pc
    reg_inst            = WORD(BUBBLE)      # WB.reg_inst
    reg_exception       = WORD(EXC_NONE)    # WB.reg_exception
    reg_rd              = WORD(0)           # WB.reg_rd
    reg_c_rf_wen        = False             # WB.reg_c_rf_wen
    reg_wbdata          = WORD(0)           # WB.reg_wbdata

    #--------------------------------------------------

    def __init__(self):
        super().__init__()
        self.bubble = False
        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.WB.pc
        #   self.inst               # Pipe.WB.inst
        #   self.exception          # Pipe.WB.exception
        #   self.rd                 # Pipe.WB.rd
        #   self.c_rf_wen           # Pipe.WB.c_rf_wen
        #   self.wbdata             # Pipe.WB.wbdata
        #
        #----------------------------------------------

    def compute(self):
        # Read out pipeline register values
        self.pc             = WB.reg_pc
        self.inst           = WB.reg_inst
        self.exception      = WB.reg_exception
        self.rd             = WB.reg_rd
        self.c_rf_wen       = WB.reg_c_rf_wen
        self.wbdata         = WB.reg_wbdata  

        if WB.reg_inst == WORD(BUBBLE):
            self.bubble = True
            return

        # nothing to compute here


    def update(self):
        if not self.bubble and self.c_rf_wen:
            Pipe.cpu.rf.write(self.rd, self.wbdata)


        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_WB, self.pc, self.inst, self.log())

        if (self.exception):
            return False
        else:
            return True
        # ------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        if self.inst == BUBBLE or (not self.c_rf_wen):
            return('# -')
        else:
            return('# R[%d] <- 0x%08x' % (self.rd, self.wbdata))
    #-----------------------------------------------------------------


