// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#pragma once

#include <initializer_list>
#include <string>

#include <frc/smartdashboard/Sendable.h>
#include <frc/smartdashboard/SendableHelper.h>
#include <wpi/ArrayRef.h>
#include <wpi/SmallSet.h>
#include <wpi/Twine.h>

#include "frc2/command/Command.h"

namespace frc2 {
/**
 * A Sendable base class for Commands.
 */
class CommandBase : public Command,
                    public frc::Sendable,
                    public frc::SendableHelper<CommandBase> {
 public:
  /**
   * Adds the specified requirements to the command.
   *
   * @param requirements the requirements to add
   */
  void AddRequirements(std::initializer_list<std::shared_ptr<Subsystem>> requirements);

  /**
   * Adds the specified requirements to the command.
   *
   * @param requirements the requirements to add
   */
  void AddRequirements(wpi::ArrayRef<std::shared_ptr<Subsystem>> requirements);

  void AddRequirements(wpi::SmallSet<std::shared_ptr<Subsystem>, 4> requirements);

  wpi::SmallSet<std::shared_ptr<Subsystem>, 4> GetRequirements() const override;

  /**
   * Sets the name of this Command.
   *
   * @param name name
   */
  void SetName(const wpi::Twine& name);

  /**
   * Gets the name of this Command.
   *
   * @return Name
   */
  std::string GetName() const override;

  /**
   * Gets the subsystem name of this Command.
   *
   * @return Subsystem name
   */
  std::string GetSubsystem() const;

  /**
   * Sets the subsystem name of this Command.
   *
   * @param subsystem subsystem name
   */
  void SetSubsystem(const wpi::Twine& subsystem);

  void InitSendable(frc::SendableBuilder& builder) override;

 protected:
  CommandBase();
  wpi::SmallSet<std::shared_ptr<Subsystem>, 4> m_requirements;
};
}  // namespace frc2
