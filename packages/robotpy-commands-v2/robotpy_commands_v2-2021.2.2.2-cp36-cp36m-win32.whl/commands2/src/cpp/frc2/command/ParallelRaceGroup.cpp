// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#include "frc2/command/ParallelRaceGroup.h"

using namespace frc2;

ParallelRaceGroup::ParallelRaceGroup(
    std::vector<std::shared_ptr<Command>>&& commands) {
  AddCommands(std::move(commands));
}

void ParallelRaceGroup::Initialize() {
  m_finished = false;
  for (auto& commandRunning : m_commands) {
    commandRunning->Initialize();
  }
  isRunning = true;
}

void ParallelRaceGroup::Execute() {
  for (auto& commandRunning : m_commands) {
    commandRunning->Execute();
    if (commandRunning->IsFinished()) {
      m_finished = true;
    }
  }
}

void ParallelRaceGroup::End(bool interrupted) {
  for (auto& commandRunning : m_commands) {
    commandRunning->End(!commandRunning->IsFinished());
  }
  isRunning = false;
}

bool ParallelRaceGroup::IsFinished() {
  return m_finished;
}

bool ParallelRaceGroup::RunsWhenDisabled() const {
  return m_runWhenDisabled;
}

void ParallelRaceGroup::AddCommands(
    std::vector<std::shared_ptr<Command>>&& commands) {
  if (!RequireUngrouped(commands)) {
    return;
  }

  if (isRunning) {
    // wpi_setWPIErrorWithContext(CommandIllegalUse,
    throw std::runtime_error(
                               "Commands cannot be added to a CommandGroup "
                               "while the group is running");
  }

  for (auto&& command : commands) {
    if (RequirementsDisjoint(this, command.get())) {
      command->SetGrouped(true);
      AddRequirements(command->GetRequirements());
      m_runWhenDisabled &= command->RunsWhenDisabled();
      m_commands.emplace_back(std::move(command));
    } else {
      // wpi_setWPIErrorWithContext(CommandIllegalUse,
      throw std::runtime_error(
                                 "Multiple commands in a parallel group cannot "
                                 "require the same subsystems");
      return;
    }
  }
}
